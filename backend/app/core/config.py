from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:rithvika@localhost:5432/resume_db"
    )
    
    class Config:
        env_file = ".env"

settings = Settings()