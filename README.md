# Customer Profile Extraction System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-green.svg)
![React](https://img.shields.io/badge/React-18.0.0+-blue.svg)

A powerful resume parsing system that extracts structured information from PDF and DOCX resumes using advanced Natural Language Processing (NLP) and Large Language Models (LLM). Built for recruiters, HR professionals, and talent acquisition teams to streamline candidate processing and analysis.

## 🌟 Features

- **Intelligent Resume Parsing**: Extract names, emails, phone numbers, and complete work experience from resumes with high accuracy
- **Bulk Processing**: Upload and analyze multiple resumes simultaneously
- **Structured Data Storage**: Store parsed information in a PostgreSQL database for easy access
- **Powerful Search**: Search through parsed profiles by name, skills, experience, and other criteria
- **CSV Export**: Export all parsed profiles to a standardized CSV format
- **Dual Interface**: Use the web interface or command-line interface based on your needs
- **Authentication & Security**: Role-based access control with JWT authentication
- **Containerized Deployment**: Easy setup with Docker and docker-compose

## 🛠️ Technology Stack

### Backend

- **FastAPI**: High-performance Python API framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Cohere LLM**: Advanced language model for accurate resume parsing
- **PyPDF2 & python-docx**: Document parsing libraries
- **Pydantic**: Data validation and settings management
- **Alembic**: Database migration tool

### Frontend

- **React**: UI library for building interactive interfaces
- **Axios**: HTTP client for API communication
- **File-Saver**: Utility for client-side file saving

### Infrastructure

- **Docker & Docker Compose**: Containerization and orchestration
- **PostgreSQL**: Relational database for data storage
- **Nginx**: Web server and reverse proxy

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Cohere API key

### Using Docker (Recommended)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/resume-parser.git
   cd resume-parser
   ```

2. **Create a `.env` file in the root directory:**

   ```
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_DB=resume_db
   COHERE_API_KEY=your_cohere_api_key
   SECRET_KEY=your_jwt_secret_key
   ```

3. **Build and start the containers:**

   ```bash
   docker-compose build
   docker-compose up
   ```

4. **Access the application:**
   - Web interface: http://localhost:3000
   - API documentation: http://localhost:8000/docs
   - Default admin credentials: admin@gmail.com / password

### Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd resume-parser/backend
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   export COHERE_API_KEY=your_cohere_api_key
   export SECRET_KEY=your_secret_key
   export DATABASE_URL=postgresql://user:password@localhost/resume_db
   ```

5. Run database migrations:

   ```bash
   alembic upgrade head
   ```

6. Run the backend server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd resume-parser/frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```
   </details>

## 📋 Usage

### Web Interface

1. **Login** with your credentials
2. **Upload** resumes through the upload interface
3. **Search** and view parsed profiles
4. **Export** selected profiles to CSV

### Command Line Interface

Process resumes in batch mode using the CLI tool:

1. **Using Docker:**

   ```bash
   docker exec -it resume-parser-backend-1 /bin/bash
   python -m app.scripts.batch_parse_and_export
   ```

2. **Local installation:**

   ```bash
   cd backend
   python -m app.scripts.batch_parse_and_export
   ```

3. When prompted, enter the path to the folder containing your resumes
4. The script will process all resumes and export a CSV to the current directory

## 📚 API Documentation

When running, the API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Key endpoints:

| Endpoint               | Method | Description                          |
| ---------------------- | ------ | ------------------------------------ |
| `/api/login`           | POST   | Authenticate user and retrieve token |
| `/api/upload-multiple` | POST   | Upload and parse multiple resumes    |
| `/api/profiles`        | GET    | Retrieve and search parsed profiles  |
| `/api/export-csv`      | GET    | Export profiles to CSV format        |

## 📁 Project Structure

```
resume-parser/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── app/
│   │   ├── api/              # API routes and endpoints
│   │   ├── core/             # Core functionality and config
│   │   ├── crud/             # Database operations
│   │   ├── db/               # Database connection and session
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── scripts/          # CLI scripts
│   │   └── main.py           # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── utils/            # Utility functions
│   │   └── App.js            # Main application component
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml        # Docker composition
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable            | Description         | Default         |
| ------------------- | ------------------- | --------------- |
| `COHERE_API_KEY`    | Your Cohere API key | None (Required) |
| `SECRET_KEY`        | JWT secret key      | None (Required) |
| `POSTGRES_USER`     | Database username   | postgres        |
| `POSTGRES_PASSWORD` | Database password   | None (Required) |
| `POSTGRES_DB`       | Database name       | resume_db       |

## 🛡️ Security Considerations

- The system uses JWT for authentication with role-based access control
- API endpoints are protected based on user roles
- Passwords are hashed securely using bcrypt
- All communication with the API should be over HTTPS in production

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Cohere](https://cohere.ai/) for their powerful language models
- [FastAPI](https://fastapi.tiangolo.com/) for the efficient API framework
- [React](https://reactjs.org/) for the frontend library
- All open-source contributors whose libraries made this project possible
