#!/bin/sh
set -e

# Wait for Postgres to be ready
until python -c "import socket; s=socket.socket(); s.connect(('db', 5432))" 2>/dev/null; do
  echo "Waiting for postgres..."
  sleep 2
done

# Run all Alembic migrations
alembic upgrade head

# Only now run the admin creation script
python -m app.scripts.create_admin

# Start the app
exec uvicorn app.main:app --host 0.0.0.0 --port 8000