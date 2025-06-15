FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install Alembic
RUN pip install alembic

# Download spaCy model
RUN python -m spacy download en_core_web_sm

COPY app/skills.csv app/skills.csv

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
