from sqlalchemy import Column, Integer, String, JSON, UniqueConstraint
from app.db.base import Base

class ResumeData(Base):
    __tablename__ = "resume_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    work_experience = Column(JSON)  # Store list of dicts as JSON

    __table_args__ = (
        UniqueConstraint('full_name', 'email', 'phone_number', name='uq_resume_data_combo'),
    )
