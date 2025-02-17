import requests
import urllib.parse
from typing import Union, Dict, Any
from pydantic import BaseModel, Field, SecretStr

from ..core.error import AuthError
from ..utils.logger import get_logger


logger = get_logger()


class Auth(BaseModel, requests.auth.AuthBase):
    """
    Auth

    This generic class will propose a common interface to all Auth
    """

    def __call__(
        self, updatable_object: Union[requests.PreparedRequest, Dict[str, Any]]
    ) -> Union[requests.PreparedRequest, Dict[str, Any]]:
        """
        Updating fields with authentication information
        This class is responsible for placing the credentials in the right places.

        Args:
            params (Union[requests.PreparedRequest, Dict[str, Any]]): updatable object

        Return:
            Union[requests.PreparedRequest, Dict[str, Any]]: updated object
        """
        return updatable_object


class NoAuth(Auth):
    """
    No Auth

    To be used if a class does not require authentication
    """

    pass


class OAuth2PasswordCredentialsBody(Auth):
    """
    OAuth2 by using a password and adding credentials in the body of the request used to get the "access token".
    """

    access_token_url: str
    client_id: str
    client_secret: SecretStr
    username: str
    password: SecretStr

    def get_access_token(self) -> str:
        """
        Get access token

        Returns:
            str: Access token
        """
        logger.debug("Getting the access token...")
        payload = dict()
        payload["grant_type"] = "password"
        payload["client_id"] = self.client_id
        payload["client_secret"] = self.client_secret.get_secret_value()
        payload["username"] = self.username
        payload["password"] = self.password.get_secret_value()

        logger.debug(
            f"Sending request to get access token (url=`{self.access_token_url}`)"
        )
        response = requests.post(self.access_token_url, data=payload)

        if not response.ok:
            logger.error("OAuth2 failed for getting access token !")
            raise AuthError("OAuth2 failed ! Reason : `{}`".format(response.content))

        logger.debug("The access token has been got")
        return response.json()["access_token"]

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        access_token = self.get_access_token()
        auth_header = {"Authorization": f"OAuth {access_token}"}
        request.headers.update(auth_header)
        return request


class XAPIKeyAuth(Auth):
    """
    X-API-Key Auth

    Auth used to authenticate with an `X-API-Key` in the headers
    """

    name: str = Field(
        "X-API-KEY",
        description="Name of the API key that will be used as a header in the request. Default value : `X-API-KEY`",
    )
    value: SecretStr = Field(..., description="API key value")

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        auth_header = {self.name: self.value.get_secret_value()}
        request.headers.update(auth_header)
        return request


class AuthorizationAuth(XAPIKeyAuth):
    """
    Authorization Auth

    Auth used to authenticate with an API key named `Authorization` in the headers
    """

    name: str = Field("Authorization", const=True)


class XSmartTokenAuth(XAPIKeyAuth):
    """
    XSmart Token Auth

    Auth used to authenticate to SmartRecruiter with a token
    """

    name: str = Field("X-SmartToken", const=True)


class OAuth2EmailPasswordBody(Auth):
    """
    OAuth2 by using a password and email to send to a sginin endpoint used to get the "access token".
    """

    access_token_url: str
    email: str
    password: SecretStr

    def get_access_token(self):

        payload = dict()
        payload["email"] = self.email
        payload["password"] = self.password.get_secret_value()
        logger.debug(
            f"Sending request to get access token (url=`{self.access_token_url}`)"
        )
        response = requests.post(self.access_token_url, data=payload)

        if not response.ok:
            logger.error("Sign in Failure !")
            raise AuthError("Signin failed ! Reason : `{}`".format(response.content))

        logger.debug("The access token has been got")
        return response.json()["access_token"]

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:

        access_token = self.get_access_token()
        auth_header = {"Authorization": f"{access_token}"}
        request.headers.update(auth_header)
        return request


class XTaleezAuth(XAPIKeyAuth):
    """
    XTaleezAuth

    Auth used to authenticate to Taleez with a token
    """

    name: str = Field("X-taleez-api-secret", const=True)


class MonsterBodyAuth(Auth):
    """
    MonsterBodyAuth

    Credentials are going to be stored on the body.
    """

    username: str = Field(description="Monster username")
    password: str = Field(description="Monster password")

    def __call__(
        self, updatable_object: requests.PreparedRequest
    ) -> requests.PreparedRequest:
        string_body = updatable_object.body.decode()
        formatted_body = string_body.format(
            username=self.username, password=self.password
        )
        encoded_body = formatted_body.encode("utf-8")
        updatable_object.body = encoded_body
        return updatable_object


class OAuth2Session(Auth):
    """
    OAuth2 by using a password and adding credentials in the body of the request used to get the "access token".
    """

    auth_code_url: str
    access_token_url: str
    session_token_url: str
    client_id: str
    client_secret: str
    username: str
    password: str
    name: str

    def get_auth_code(self):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "action": "Login",
            "username": self.username,
            "password": self.password,
        }
        resp_auth = requests.post(self.auth_code_url, params=params)
        url = resp_auth.url
        query = urllib.parse.urlparse(url).query
        params_dict = urllib.parse.parse_qs(query)
        if "code" not in params_dict:
            raise AuthError("Can't find the auth_code.")
        return params_dict["code"][0]

    def get_access_token(self, auth_code:str):
        params = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        resp_token = requests.post(self.access_token_url, params=params)
        return resp_token.json()["access_token"]

    def get_session_token(self, access_token:str):
        params = {"version": "*", "access_token": access_token}
        session_token = requests.post(self.session_token_url, params=params)
        return session_token.json()["BhRestToken"]

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        auth_code = self.get_auth_code()
        access_token = self.get_access_token(auth_code)
        session_token = self.get_session_token(access_token)
        auth_header = {"BhRestToken": session_token}
        request.headers.update(auth_header)
        return request
