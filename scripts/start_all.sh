#!/bin/bash

# This script starts the local application components (database, backend, frontend)
# in separate terminal windows.

# Ensure we are in the project root
PROJECT_ROOT="/Users/jepperasmussen/Documents/workspace/github.com/jepras/gcp-infrastructure"
cd "$PROJECT_ROOT" || { echo "Error: Could not change to project root."; exit 1; }

echo "Starting local application components..."

# --- 1. Start Database (Docker Compose) ---
echo "Starting database with Docker Compose..."
docker compose up -d db

# Give the database a moment to start up
sleep 5

# --- 2. Start Backend ---
echo "Starting backend in a new terminal window..."
BACKEND_CMD="cd "$PROJECT_ROOT" && source venv/bin/activate && set -a; source .env; set +a && python -m alembic upgrade head && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080"
osascript -e "tell application "Terminal" to do script "$BACKEND_CMD""

# Give the backend a moment to start up
sleep 5

# --- 3. Start Frontend ---
echo "Starting frontend in a new terminal window..."
FRONTEND_CMD="cd "$PROJECT_ROOT/frontend" && npm install && npm run dev"
osascript -e "tell application "Terminal" to do script "$FRONTEND_CMD""

echo "All components are attempting to start. Check the new terminal windows for status."
echo "You can close this window now."
