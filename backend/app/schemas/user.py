from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserLogin(UserBase):
    password: str

class User(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False

    class Config:
        from_attributes = True  # For Pydantic v2