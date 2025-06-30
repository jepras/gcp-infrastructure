# Project Implementation Tasks

This document breaks down the project implementation into verifiable phases and steps for both local and production environments.

---

## Phase 0: Project & Cloud Foundation (One-Time Setup)

**Goal**: Prepare the cloud environment and local project structure.

-   [x] **Local**: Initialize a Git repository.
-   [x] **Local**: Create the top-level directory structure (`backend/`, `frontend/`, `docs/`, `scripts/`).
-   [x] **Production**: Create a new project in the Google Cloud Console.
-   [x] **Production**: Link the GCP project to a new Firebase project.
-   [x] **Production**: Enable required GCP APIs: Cloud Run, Secret Manager, Artifact Registry, Cloud Build.
-   [x] **Production**: Create a serverless PostgreSQL database project (e.g., on Neon).
-   [x] **Production**: Register OAuth applications for Outlook and Pipedrive in their respective developer portals. Note the Client IDs and Secrets.

---

## Phase 1: The "Walking Skeleton" - Auth & Deployment

**Goal**: Get a minimal, authenticated application deployed to prove the end-to-end pipeline works.

### Local Environment

-   [x] **Backend**: Create a basic FastAPI app with a single protected endpoint (`/api/profile`).
-   [x] **Backend**: Implement the `firebase_auth.py` dependency to verify tokens.
-   [x] **Frontend**: Create a basic Next.js app.
-   [x] **Frontend**: Implement the Firebase SDK and `AuthProvider` to manage user login state.
-   [x] **Frontend**: Create a simple login page and a profile page that calls the backend's protected endpoint.
-   [x] **Local**: Create a `docker-compose.yml` file to run the backend and a local PostgreSQL database.

### Production Environment

-   [x] **Production**: Create secrets in Google Secret Manager for `CREDENTIAL_ENCRYPTION_KEY` and `GOOGLE_APPLICATION_CREDENTIALS`.
-   [x] **Production**: Add the Neon database connection string as a secret named `DATABASE_URL`.
-   [x] **Production**: Configure Firebase Authentication in the console (e.g., enable Google Sign-In).
-   [x] **Production**: Run the `scripts/deploy.sh` script for the first time.
-   [x] **Verification**: Log in to the deployed production frontend and confirm that the profile page successfully fetches data from the backend.

---

## Phase 2: Database & Core Models

**Goal**: Establish the database schema and migration process.

### Local Environment

-   [x] **Backend**: Define the SQLAlchemy models for `User` and `Credential` in `backend/app/models/database.py`.
-   [x] **Backend**: Set up Alembic to manage database migrations.
-   [x] **Backend**: Create an initial migration (`alembic revision --autogenerate`) to create the tables.
-   [x] **Backend**: Run `alembic upgrade head` locally (via `docker-compose`) to apply the migration to the local database.

### Production Environment

-   [x] **Backend**: Implement the `scripts/start.sh` script to run `alembic upgrade head` before the server starts.
-   [x] **Backend**: Update the `Dockerfile` to use `scripts/start.sh` as its `CMD`.
-   [x] **Production**: Deploy the updated application.
-   [x] **Verification**: Check the Cloud Run logs to confirm the database migration ran successfully on startup.

---

## Phase 3: Service Authentication (OAuth Flows) ✅ COMPLETED

**Goal**: Allow users to securely connect their external service accounts.

### Local Environment

-   [x] **Backend**: Implement the `encryption.py` service for encrypting/decrypting tokens.
-   [x] **Backend**: Create API endpoints to initiate the OAuth flows for Outlook and Pipedrive (e.g., `/api/auth/connect/outlook`).
-   [x] **Backend**: Create the callback endpoints (`/api/auth/callback/outlook`) to handle the response, exchange the code for tokens, encrypt them, and save them to the database.
-   [x] **Frontend**: Build the UI components (e.g., "Connect" buttons) that link to the backend's OAuth initiation endpoints.
-   [x] **Backend**: Implement session-based OAuth flow with proper user identification.
-   [x] **Backend**: Add CORS middleware for local development.
-   [x] **Backend**: Create test endpoints to verify API connectivity (e.g., `/api/test-pipedrive`).
-   [x] **Verification**: Successfully connect Pipedrive account and verify API calls work.

### Production Environment

-   [ ] **Production**: Update the redirect URIs in the Outlook and Pipedrive app configurations to point to the production Cloud Run service URL.
-   [ ] **Production**: Add the OAuth Client IDs and Secrets to Google Secret Manager.
-   [ ] **Production**: Deploy the updated application.
-   [ ] **Verification**: Go through the full connection flow on the production site for both Outlook and Pipedrive.

---

## Phase 4: Core Logic (Email to Deal) 🚀 READY TO START

**Goal**: Implement the primary business logic of the application.

### Local Environment

-   [ ] **Backend**: Create the `PipedriveService` and `OutlookService` classes to interact with their respective APIs.
-   [ ] **Backend**: Implement the LangChain-powered `AIAnalyzer` service.
-   [ ] **Backend**: Create the `EmailProcessor` service that orchestrates the entire flow: fetch email -> analyze -> create deal.
-   [ ] **Backend**: Implement the Outlook webhook endpoint.
-   [ ] **Backend**: Write unit tests for the services, mocking external API calls.

### Production Environment

-   [ ] **Production**: Deploy the application with the full core logic.
-   [ ] **Production**: Configure the Outlook webhook subscription to point to the production webhook endpoint.
-   [ ] **Verification**: Send a test email to a connected Outlook account and verify that a deal is created in the corresponding Pipedrive account.