from sqlalchemy import Column, Integer, String, JSON
from app.db.base import Base

class ResumeData(Base):
    __tablename__ = "resume_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    title = Column(String)
    contact = Column(JSON)
    experience = Column(JSON)
    education = Column(JSON)
    skills = Column(String)
    all_links = Column(JSON)
