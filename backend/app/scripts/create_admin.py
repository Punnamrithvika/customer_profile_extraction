from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@gmail.com").first()
        if existing:
            print("Admin user already exists.")
            return
        hashed_password = pwd_context.hash("admin")  # Replace with your desired password
        admin_user = User(
            email="admin@gmail.com",
            hashed_password=hashed_password,
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

def create_regular_user(email: str, password: str):
    db = SessionLocal()
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        is_admin=False  # Regular user
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    print(f"User {email} created.")

if __name__ == "__main__":
    create_admin()
    create_regular_user("user1@gmail.com", "user1")