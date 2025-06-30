#!/bin/bash

# This script is responsible for starting the frontend application.

cd frontend
export NEXT_PUBLIC_BACKEND_URL="http://localhost:8080"
npm install # Ensure dependencies are installed
echo "NEXT_PUBLIC_BACKEND_URL set to: $NEXT_PUBLIC_BACKEND_URL"
npm run build # Build the frontend for the correct backend URL
npm run dev
