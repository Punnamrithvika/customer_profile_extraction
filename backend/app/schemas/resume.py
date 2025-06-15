from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Contact(BaseModel):
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str] = ""
    links: Optional[List[str]] = []

class ExperienceEntry(BaseModel):
    customer: Optional[str]
    role: Optional[str]
    project_dates: Optional[str]
    technology: Optional[List[str]] = []

class EducationEntry(BaseModel):
    institution: Optional[str]
    degree: Optional[str]
    date: Optional[str]

class ResumeDataBase(BaseModel):
    name: Optional[str]
    title: Optional[str]
    contact: Optional[Contact] = None
    experience: Optional[List[ExperienceEntry]] = []
    education: Optional[List[EducationEntry]] = []
    skills: Optional[str]
    all_links: Optional[List[str]] = []

class ResumeDataCreate(ResumeDataBase):
    pass

class ResumeData(ResumeDataBase):
    id: int

    class Config:
        from_attributes = True
