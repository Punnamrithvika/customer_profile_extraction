from app.db.base import Base  # Import the single shared Base

from .resume import ResumeData
from .user import User

__all__ = ['Base', 'ResumeData', 'User']