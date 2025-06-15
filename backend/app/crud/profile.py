from sqlalchemy import func, String
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.resume import ResumeData  # Updated import
from app.schemas.resume import ResumeDataCreate  # Updated import

def get_profile_by_email(db: Session, email: str):
    return db.query(ResumeData).filter(ResumeData.contact['email'].cast(String) == email).first()

def get_profiles(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(ResumeData)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            func.lower(ResumeData.name).like(search_lower) |
            func.lower(ResumeData.contact['email'].cast(String)).like(search_lower) |
            func.lower(ResumeData.skills).like(search_lower)
        )
    return query.offset(skip).limit(limit).all()

def create_profile(db: Session, profile: ResumeDataCreate):
    try:
        db_profile = ResumeData(**profile.dict())
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except SQLAlchemyError as e:
        db.rollback()
        import traceback
        print(f"Database error: {e}")
        traceback.print_exc()
        raise
    except Exception as e:
        db.rollback()
        import traceback
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        raise
