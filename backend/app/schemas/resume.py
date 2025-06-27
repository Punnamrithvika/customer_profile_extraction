from typing import List, Optional
from pydantic import BaseModel

class WorkExperienceEntry(BaseModel):
    company_name: Optional[str] = None
    customer_name: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    skills_technologies: Optional[List[str]] = []
    industry_domain: Optional[str] = None
    location: Optional[str] = None

class ResumeDataBase(BaseModel):
    id: Optional[int] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    work_experience: Optional[List[WorkExperienceEntry]] = []

class ResumeDataCreate(ResumeDataBase):
    pass

class ResumeData(ResumeDataBase):
    class Config:
        from_attributes = True
