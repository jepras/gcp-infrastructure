#!/bin/bash

# This script is responsible for starting the backend application.
# Run database migrations before starting the server.

# Kill any process running on port 8080
lsof -t -i :8080 | xargs kill -9 2>/dev/null || true
sleep 1

# Load environment variables from .env file for local development
set -a; source .env; set +a

# Ensure DATABASE_URL is available (from Secret Manager)
if [ -z "$DATABASE_URL" ]; then
  echo "Error: DATABASE_URL environment variable not set. Cannot run migrations."
  exit 1
fi

# Run Alembic migrations
python -m alembic upgrade head

# Start the FastAPI application using Uvicorn
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

