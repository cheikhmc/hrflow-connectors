from typing import Optional, Dict, Any, List
from pydantic import BaseModel

# Job model
class SAPSuccessFactorsJobRequistion(BaseModel):
    annual_SA: Optional[str]
    location: Optional[str]
    city: Optional[str] = None
    country: Optional[str] = None
    department: Optional[str] = None
    division: Optional[str] = None
    facility: Optional[str] = None
    function: Optional[str] = None
    industry: Optional[str] = None
    monthly_salary: Optional[str] = None
    salaryBase: Optional[str] = None
    otherBonus: Optional[str] = None
    salaryMax: Optional[str] = None
    salaryMin: Optional[str] = None
    stateProvince: Optional[str] = None
    jobStartDate: Optional[str] = None
    recruiterTeam: Optional[Dict[str, Any]] = None
    hiringManagerTeam: Optional[Dict[str, Any]] = None
    sourcerTeam: Optional[Dict[str, Any]] = None


class SAPSuccessFactorsJob(BaseModel):
    jobDescription: Optional[str]
    jobTitle: Optional[str]
    jobReqId: Optional[str]
    jobRequisition: SAPSuccessFactorsJobRequistion


# Profile model


class Result(BaseModel):

    endDate: Optional[str]
    school: str
    schoolAddress: str
    startDate: Optional[str]


class Education(BaseModel):
    results: List[Result]


class ResultLanguage(BaseModel):
    language: str
    readingProf: str
    speakingProf: str
    writingProf: str


class Languages(BaseModel):
    results: List[ResultLanguage]


class ResultOutsideWorkExperience(BaseModel):
    employer: Optional[str]
    employerAddress: str
    endDate: Optional[str]
    startDate: Optional[str]


class OutsideWorkExperience(BaseModel):
    results: List[ResultOutsideWorkExperience]


class InsideWorkExperienceResult(BaseModel):
    backgroundElementId: Optional[str]
    bgOrderPos: Optional[str]
    candidateId: Optional[str]
    department: Optional[str]
    endDate: Optional[str]
    lastModifiedDateTime: Optional[str]
    startDate: Optional[str]
    title: Optional[str]
    candidate: Optional[str]


class InsideWorkExperience(BaseModel):
    results: List[InsideWorkExperienceResult]


class TalentPoolResults(BaseModel):
    startDate: Optional[str]
    talentPoolComments: Optional[str]
    talentPoolStatus: Optional[str]
    talentPoolitem: Optional[str]


class TalentPool(BaseModel):
    results: List[TalentPoolResults]


class SapCandidateModel(BaseModel):
    address: str
    cellPhone: Optional[str]
    city: Optional[str]
    contactEmail: Optional[str]
    country: str
    creationDateTime: Optional[str]
    currentTitle: Optional[str]
    dateofAvailability: Optional[str]
    firstName: str
    homePhone: Optional[str]
    lastName: str
    middleName: Optional[str]
    partnerMemberId: Optional[str]
    partnerSource: Optional[str]
    primaryEmail: str
    zip: Optional[str]
    education: Optional[Education]
    languages: Optional[Languages]
    outsideWorkExperience: Optional[OutsideWorkExperience]
    insideWorkExperience: Optional[InsideWorkExperience]
    talentPool: Optional[TalentPool]
