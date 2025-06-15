from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import SessionLocal
from app.models.resume import ResumeData  # <-- Use SQLAlchemy model for DB queries
from app.schemas.resume import ResumeData as ResumeDataSchema  # <-- Use Pydantic schema for response

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/resumes", response_model=List[ResumeDataSchema])
def get_resumes(db: Session = Depends(get_db)):
    return db.query(ResumeData).all()
