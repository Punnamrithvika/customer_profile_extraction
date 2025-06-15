import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from io import StringIO
from typing import List
from jose import jwt, JWTError

from app.db.session import SessionLocal
from app.schemas.resume import ResumeData, ResumeDataCreate
from app.crud import profile as crud
from app.core.parser import parse_resume, postprocess_resume_skills, TECH_KEYWORDS
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

@router.post("/upload", response_model=ResumeData)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are supported.")
    
    file_bytes = await file.read()
    
    try:
        extracted_data = parse_resume(file_bytes, file.filename)
        extracted_data = postprocess_resume_skills(extracted_data, TECH_KEYWORDS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {e}")

    # Use nested contact object for email
    email = extracted_data.get("contact", {}).get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Could not extract email from the resume.")
    
    db_profile = crud.get_profile_by_email(db, email=email)
    if db_profile:
        raise HTTPException(status_code=400, detail="Email already registered.")
    
    # Ensure all fields are present for ResumeDataCreate
    all_fields = [
        "name", "title", "contact", "experience", "education", "skills", "all_links"
    ]
    for field in all_fields:
        if field not in extracted_data:
            if field in ["experience", "education", "all_links"]:
                extracted_data[field] = []
            elif field == "contact":
                extracted_data[field] = {}
            else:
                extracted_data[field] = None
    profile_to_create = ResumeDataCreate(**extracted_data)
    return crud.create_profile(db=db, profile=profile_to_create)

@router.get("/", response_model=List[ResumeData])
def read_profiles(skip: int = 0, limit: int = 100, search: str = Query(None), db: Session = Depends(get_db)):
    profiles = crud.get_profiles(db, skip=skip, limit=limit, search=search.lower() if search else None)
    return profiles

@router.get("/export-csv")
def export_profiles_to_csv(search: str = Query(None), db: Session = Depends(get_db)):
    profiles = crud.get_profiles(db, limit=1000, search=search.lower() if search else None) # Export up to 1000
    
    if not profiles:
        raise HTTPException(status_code=404, detail="No profiles found for the given criteria.")

    profile_dicts = [
        {
            "name": p.name,
            "email": p.contact.get("email") if p.contact else "",
            "phone": p.contact.get("phone") if p.contact else "",
            "skills": p.skills
        } for p in profiles
    ]
    df = pd.DataFrame(profile_dicts)
    
    stream = StringIO()
    df.to_csv(stream, index=False)
    
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=profiles.csv"
    return response

@router.get("/profiles", response_model=List[ResumeData])
def read_profiles_profiles(skip: int = 0, limit: int = 100, search: str = Query(None), db: Session = Depends(get_db)):
    return read_profiles(skip=skip, limit=limit, search=search, db=db)

@router.post("/profiles/upload", response_model=ResumeData)
async def upload_resume_profiles(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    file_bytes = await file.read()
    extracted_data = parse_resume(file_bytes, file.filename)
    extracted_data = postprocess_resume_skills(extracted_data, TECH_KEYWORDS)
    
    all_fields = [
        "name", "title", "contact", "experience", "education", "skills", "all_links"
    ]
    for field in all_fields:
        if field not in extracted_data:
            if field in ["experience", "education", "all_links"]:
                extracted_data[field] = []
            elif field == "contact":
                extracted_data[field] = {}
            else:
                extracted_data[field] = None

    profile_to_create = ResumeDataCreate(**extracted_data)
    db_profile = crud.create_profile(db=db, profile=profile_to_create)
    return db_profile

@router.get("/profiles/export-csv")
def export_profiles_to_csv_profiles(search: str = Query(None), db: Session = Depends(get_db)):
    return export_profiles_to_csv(search=search, db=db)
