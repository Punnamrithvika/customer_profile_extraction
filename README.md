# Customer Profile Extraction System MVP

This project is a full-stack Minimum Viable Product for extracting customer profiles from resumes. It features:
- **Backend:** FastAPI (Python)
- **Frontend:** ReactJS
- **Database:** PostgreSQL
- **NLP:** spaCy, PyMuPDF, python-docx
- **Containerization:** Docker Compose

## Features
- Upload resumes (PDF/DOCX)
- Extract name, email, phone, skills
- Store and search profiles by skill
- Export profiles to CSV

## How to Run
1. Ensure Docker and Docker Compose are installed.
2. In the project root, run:
   ```zsh
   docker-compose up --build
   ```
3. Access the frontend at [http://localhost:3000](http://localhost:3000)
4. Access the backend API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## Development
- For local frontend: `cd frontend && npm install && npm start`
- For local backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`

---

See the project documentation for more details.
