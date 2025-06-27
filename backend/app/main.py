from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base
from app.api.endpoints import profiles, auth, users
from app.api import routes
from app.models import Base, User, ResumeData  # Import all models!

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Profile Extractor")

# CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router, prefix="/api", tags=["profiles"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(routes.router, prefix="/api", tags=["routes"])
app.include_router(users.router, prefix="/api", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Customer Profile Extractor API"}
