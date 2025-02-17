from typing import Iterator, Dict, Any, Optional
from pydantic import Field
import requests

from ...core.error import PullError, PushError
from ...core.action import PullJobsBaseAction, PushProfileBaseAction
from ...utils.logger import get_logger
from ...utils.clean_text import remove_html_tags
from ...utils.hrflow import generate_workflow_response
from ...core.auth import AuthorizationAuth
from ...utils.schemas import HrflowJob, HrflowProfile
from .schemas import TeamtailorJob, TeamtailorCandidateAttribute

logger = get_logger()


class PullJobsAction(PullJobsBaseAction):
    auth: AuthorizationAuth

    def pull(self) -> Iterator[TeamtailorJob]:
        """
        Pull all jobs from a Teamtailor job board
        Returns:
            Iterator[TeamtailorJob]: list of all jobs with their content if available
        """
        # Prepare request
        session = requests.Session()
        pull_jobs_request = requests.Request()
        pull_jobs_request.method = "GET"
        pull_jobs_request.url = "https://api.teamtailor.com/v1/jobs"
        pull_jobs_request.auth = self.auth
        pull_jobs_request.headers = {"X-Api-Version": "20210218"}
        prepared_request = pull_jobs_request.prepare()

        # Send request
        response = session.send(prepared_request)

        if not response.ok:
            raise PullError(
                response,
                message="Failed to get jobs from Teamtailor.",
            )

        response_dict = response.json()

        job_list = response_dict["data"]
        job_obj_list = map(TeamtailorJob.parse_obj, job_list)
        return job_obj_list

    def format(self, data: TeamtailorJob) -> HrflowJob:
        """
        Format a Teamtailor job object into a Hrflow job object

        Args:
            data (TeamtailorJob): Teamtailor job object from the list of jobs pulled

        Returns:
            HrflowJob: a job in the HrFlow job object form
        """
        job = dict()
        data = data.dict()
        attribute = data.get("attributes")
        job["name"] = attribute.get("title")
        job["reference"] = data.get("id")
        job["summary"] = attribute.get("pitch")
        job["created_at"] = attribute.get("created-at")
        job["updated_at"] = attribute.get("updated-at")
        job["url"] = data.get("links").get("careersite-job-url")

        # get location request
        job["location"] = dict(text=None, lat=None, lng=None)

        def get_location() -> None:
            """
            Get_location sends a request to get the job location from its API endpoint
            """
            session = requests.Session()
            pull_job_location_request = requests.Request()
            pull_job_location_request.method = "GET"
            id = job["reference"]
            pull_job_location_request.url = (
                f"https://api.teamtailor.com/v1/jobs/{id}/location"
            )

            pull_job_location_request.headers = {"X-Api-Version": "20210218"}
            pull_job_location_request.auth = self.auth
            prepared_request = pull_job_location_request.prepare()
            response = session.send(prepared_request)
            if not response.ok:
                raise PullError(
                    response,
                    message="Failed to get job location from Teamtailor.",
                )
            location = response.json().get("data")
            if location is not None:
                location_attribute = location.get("attributes")
                text = location_attribute["address"]
                city = location_attribute["city"]
                country = location_attribute["country"]
                headquarters = location_attribute["headquarters"]
                lat = location_attribute["lat"]
                lng = location_attribute["long"]
                zip = location_attribute["zip"]
                name = location_attribute["name"]
                geojson = dict(
                    city=city,
                    country=country,
                    headquarters=headquarters,
                    zip=zip,
                    name=name,
                )
                job["location"] = dict(text=text, geojson=geojson, lat=lat, lng=lng)

        get_location()

        # sections
        description = remove_html_tags(attribute.get("body"))
        job["sections"] = [
            dict(
                name="teamtailor_description",
                title="teamtailor_description",
                description=description,
            )
        ]
        # tags
        job["tags"] = []

        def create_tag(field_name: str) -> None:
            tag_name = "teamtailor_{}".format(field_name)
            tag_value = attribute.get(field_name)

            if tag_value is not None:
                tag = dict(name=tag_name, value=tag_value)
                job["tags"].append(tag)

        create_tag("start-date")
        create_tag("end-date")
        create_tag("status")
        create_tag("employment-type")
        create_tag("employment-level")
        create_tag("remote-status")
        create_tag("salary-time-unit")
        create_tag("min-salary")
        create_tag("max-salary")
        create_tag("currency")
        create_tag("internal")

        job_obj = HrflowJob.parse_obj(job)
        return job_obj


class PushProfileAction(PushProfileBaseAction):

    auth: AuthorizationAuth
    sourced: Optional[bool] = Field(
        False, description="True if added by a recruiter without applying"
    )

    def format(self, data: HrflowProfile) -> TeamtailorCandidateAttribute:
        """
        Format a Hrflow profile object into a Teamtailor profile object

        Args:
            data (HrflowProfile): Hrflow Profile to format

        Returns:
            Dict[str, Any]: a Teamtailor formatted profile object
        """
        profile = dict()
        data = data.dict()
        info = data.get("info")
        profile["first-name"] = info.get("first_name")
        profile["last-name"] = info.get("last_name")
        profile["email"] = info.get("email")
        profile["phone"] = info.get("phone")
        profile["pitch"] = info.get("summary")
        resume = data.get("attachments")[1]
        profile["resume"] = resume.get("public_url")
        profile["sourced"] = self.sourced
        profile["tags"] = data.get("tags")
        profile_obj = TeamtailorCandidateAttribute.parse_obj(profile)

        return profile_obj

    def push(self, data: TeamtailorCandidateAttribute):
        """
        Push a Hrflow profile object to a Teamtailor candidate pool for a position

        Args:
            data (TeamtailorCandidateAttribute): profile to push
        """
        profile = next(data)
        profile = profile.dict()
        profile["first-name"] = profile.pop("first_name")
        profile["last-name"] = profile.pop("last_name")
        profile_json = dict(data=dict(type="candidates", attributes=profile))
        auth = self.auth
        request_url = "https://api.teamtailor.com/v1/candidates"

        session = requests.Session()

        def send_request(
            method: str,
            url: str,
            error_message: str,
            params: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
        ) -> requests.Response:
            """
            Send a HTTPS request to the specified url using the specified paramters
            Args:
                method (str): request method: "GET", "PUT", "POST"...
                url (str): url endpoint to receive the request
                error_message (str): message to be displayed when a `PushError` error is raised
                json (optional): data to be sent to the endpoint. Defaults to None.
                params (optional): additional parameters to the request
                return_response (optional): In case we want to the function to return the response. Defaults to None.
            Returns:
                Response (requests.Response)
            """
            request = requests.Request()
            request.method = method
            request.url = url
            request.auth = auth
            request.headers = {
                "X-Api-Version": "20210218",
                "content-type": "application/vnd.api+json",
            }
            if json is not None:
                request.json = json
            if params is not None:
                request.params = params
            prepared_request = request.prepare()
            response = session.send(prepared_request)
            if not response.ok:
                raise PushError(response, message=error_message)

            return response

        # a request to verify if the candidate profile already exist
        get_candidate_param = {"filter[email]": f'{profile.get("email")}'}
        get_candidate_response = send_request(
            method="GET",
            url=request_url,
            params=get_candidate_param,
            error_message="Failed to get candidate",
        )
        candidate_list = get_candidate_response.json().get("data")
        candidate = None
        if candidate_list != []:
            candidate = candidate_list[0]

        # In case the candidate exists we retrieve his id to update his profile with a "PUT" request
        if candidate is not None:
            candidate_id = candidate["id"]
            logger.info(f"Candidate Already exists with the id {candidate_id}")
            update_profile_url = request_url + f"/{candidate_id}"
            profile_json["data"]["id"] = candidate_id
            logger.info("Updating Candidate profile")
            send_request(
                method="PATCH",
                url=update_profile_url,
                json=profile_json,
                error_message="Failed to update candidate profile",
            )
        # If the candidate doesn't already exist we "POST" his profile
        else:
            # Post profile request
            logger.info("Preparing request to push candidate profile")
            send_request(
                method="POST",
                url=request_url,
                json=profile_json,
                error_message="Failed to post candidate profile",
            )
