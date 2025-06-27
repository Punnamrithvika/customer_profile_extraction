from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(email, password, is_admin=False):
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User with email {email} already exists.")
            return
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        db.add(user)
        db.commit()
        print(f"{'Admin' if is_admin else 'Regular'} user '{email}' created successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_user("admin@gmail.com", "admin", is_admin=True)
    create_user("user1@gmail.com", "user1", is_admin=False)