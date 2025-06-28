#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration Variables ---
PROJECT_ID="gcp-infrastructure-464305" # Your Google Cloud Project ID
FIREBASE_PROJECT_ID="gcp-infrastructure-464305" # Your Firebase Project ID (often same as GCP Project ID)
REGION="us-central1" # Google Cloud Run region
SERVICE_NAME="ai-email-processor-backend" # Name of your Cloud Run service

# --- 1. Get Git Commit Hash for Versioning ---
GIT_COMMIT=$(git rev-parse --short HEAD)
IMAGE_TAG="gcr.io/${PROJECT_ID}/ai-email-processor-backend:${GIT_COMMIT}"

echo "🚀 Starting deployment for commit: ${GIT_COMMIT}"

# --- 2. Build and Push Backend Docker Image to Artifact Registry ---

# Configure Docker to use gcloud as a credential helper
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud auth configure-docker

echo "🏗️ Building backend Docker image..."
docker build -t ${IMAGE_TAG} ./backend

echo "📤 Pushing backend Docker image to Artifact Registry..."
docker push ${IMAGE_TAG}

# --- 3. Deploy Backend to Google Cloud Run ---

# Get the service account email for the default compute service account
SERVICE_ACCOUNT_EMAIL=$(/Users/jepperasmussen/google-cloud-sdk/bin/gcloud iam service-accounts list \
  --filter="displayName:Compute Engine default service account" \
  --format="value(email)")

# Grant Secret Manager access to the service account if it doesn't have it
# This command will only add the binding if it doesn't exist
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" \
  --condition=None || true # Use || true to prevent script from exiting if binding already exists

echo "🚀 Deploying backend service to Cloud Run..."
/Users/jepperasmussen/google-cloud-sdk/bin/gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_TAG} \
  --region ${REGION} \
  --platform managed \
  --allow-unauthenticated \
  --service-account ${SERVICE_ACCOUNT_EMAIL} \
  --set-secrets=DATABASE_URL=DATABASE_URL:latest,CREDENTIAL_ENCRYPTION_KEY=CREDENTIAL_ENCRYPTION_KEY:latest,GOOGLE_APPLICATION_CREDENTIALS=GOOGLE_APPLICATION_CREDENTIALS:latest,OUTLOOK_CLIENT_ID=OUTLOOK_CLIENT_ID:latest,OUTLOOK_CLIENT_SECRET=OUTLOOK_CLIENT_SECRET:latest,PIPEDRIVE_CLIENT_ID=PIPEDRIVE_CLIENT_ID:latest,PIPEDRIVE_CLIENT_SECRET=PIPEDRIVE_CLIENT_SECRET:latest \
  --port 8080 \
  --project ${PROJECT_ID}

# Get the Cloud Run service URL
CLOUD_RUN_URL=$(/Users/jepperasmussen/google-cloud-sdk/bin/gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --format="value(status.url)" \
  --project ${PROJECT_ID})

echo "Backend deployed to: ${CLOUD_RUN_URL}"

# --- 4. Build and Deploy Frontend to Firebase Hosting ---

echo "🏗️ Building frontend application..."
npm --prefix ./frontend run build

echo "📤 Deploying frontend to Firebase Hosting..."
/Users/jepperasmussen/google-cloud-sdk/bin/firebase deploy --project ${FIREBASE_PROJECT_ID} --only hosting

echo "✅ Deployment complete!"
