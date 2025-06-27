import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from io import StringIO
from typing import List
from jose import jwt, JWTError
import json

from app.db.session import SessionLocal
from app.schemas.resume import ResumeData, ResumeDataCreate
from app.crud import profile as crud
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer
from app.core.parser import parse_resume 

from typing import List
from fastapi import UploadFile

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
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx") or file.filename.endswith(".doc")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are supported.")
    
    file_bytes = await file.read()

    try:
        extracted_data = parse_resume(file_bytes, file.filename)
        # Map parser output to schema fields
        mapped_data = {
            "full_name": extracted_data.get("full_name"),
            "email": extracted_data.get("email"),
            "phone_number": extracted_data.get("phone_number"),
            "work_experience": extracted_data.get("work_experience", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {e}")

    if not mapped_data["email"] or not mapped_data["phone_number"]:
        raise HTTPException(status_code=400, detail="Could not extract email or phone number from the resume.")
    
    db_profile = crud.get_profile_by_email_and_phone(db, email=mapped_data["email"], phone_number=mapped_data["phone_number"])
    if db_profile:
        raise HTTPException(status_code=400, detail="Email and phone number already registered.")
    
    profile_to_create = ResumeDataCreate(**mapped_data)
    return crud.create_profile(db=db, profile=profile_to_create)

@router.get("/", response_model=List[ResumeData])
def read_profiles(skip: int = 0, limit: int = 100, search: str = Query(None), db: Session = Depends(get_db)):
    profiles = crud.get_profiles(db, skip=skip, limit=limit, search=search.lower() if search else None)
    return profiles

@router.get("/export-csv")
def export_profiles_to_csv(search: str = Query(None), db: Session = Depends(get_db)):
    profiles = crud.get_profiles(db, limit=1000, search=search.lower() if search else None)
    if not profiles:
        raise HTTPException(status_code=404, detail="No profiles found for the given criteria.")

    profile_dicts = [
        {
            "full_name": p.full_name,
            "email": p.email,
            "phone_number": p.phone_number,
            "work_experience": json.dumps(p.work_experience)
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
    try:
        extracted_data = parse_resume(file_bytes, file.filename)
        # Map parser output to schema fields
        mapped_data = {
            "full_name": extracted_data.get("Full Name"),
            "email": extracted_data.get("Email"),
            "phone_number": extracted_data.get("Phone Number"),
            "work_experience": extracted_data.get("Work Experience"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {e}")

    if not mapped_data["email"]:
        raise HTTPException(status_code=400, detail="Could not extract email from the resume.")

    db_profile = crud.get_profile_by_email(db, email=mapped_data["email"])
    if db_profile:
        raise HTTPException(status_code=400, detail="Email already registered.")

    profile_to_create = ResumeDataCreate(**mapped_data)
    db_profile = crud.create_profile(db=db, profile=profile_to_create)
    return db_profile

@router.get("/profiles/export-csv")
def export_profiles_to_csv_profiles(search: str = Query(None), db: Session = Depends(get_db)):
    return export_profiles_to_csv(search=search, db=db)

@router.post("/upload-multiple")
async def upload_multiple_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    results = []
    errors = []
    for file in files:
        try:
            file_bytes = await file.read()
            extracted_data = parse_resume(file_bytes, file.filename)
            mapped_data = {
                "full_name": extracted_data.get("full_name"),
                "email": extracted_data.get("email"),
                "phone_number": extracted_data.get("phone_number"),
                "work_experience": extracted_data.get("work_experience", []),
            }
            if not (mapped_data["full_name"] or mapped_data["email"] or mapped_data["phone_number"]):
                errors.append(f"{file.filename}: Could not extract name, email, or phone number.")
                continue

            db_profile = crud.get_profile_by_all_keys(
                db,
                full_name=mapped_data["full_name"],
                email=mapped_data["email"],
                phone_number=mapped_data["phone_number"]
            )
            if db_profile:
                errors.append(f"{file.filename}: User with same name, email, and phone number already exists.")
                continue
            profile_to_create = ResumeDataCreate(**mapped_data)
            crud.create_profile(db=db, profile=profile_to_create)
            results.append({"filename": file.filename, "status": "success"})
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    return {"results": results, "errors": errors}
