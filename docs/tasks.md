# Project Implementation Tasks

This document breaks down the project implementation into verifiable phases and steps for both local and production environments.

---

## Phase 0: Project & Cloud Foundation (One-Time Setup)

**Goal**: Prepare the cloud environment and local project structure.

-   [ ] **Local**: Initialize a Git repository.
-   [ ] **Local**: Create the top-level directory structure (`backend/`, `frontend/`, `docs/`, `scripts/`).
-   [ ] **Production**: Create a new project in the Google Cloud Console.
-   [ ] **Production**: Link the GCP project to a new Firebase project.
-   [ ] **Production**: Enable required GCP APIs: Cloud Run, Secret Manager, Artifact Registry, Cloud Build.
-   [ ] **Production**: Create a serverless PostgreSQL database project (e.g., on Neon).
-   [ ] **Production**: Register OAuth applications for Outlook and Pipedrive in their respective developer portals. Note the Client IDs and Secrets.

---

## Phase 1: The "Walking Skeleton" - Auth & Deployment

**Goal**: Get a minimal, authenticated application deployed to prove the end-to-end pipeline works.

### Local Environment

-   [ ] **Backend**: Create a basic FastAPI app with a single protected endpoint (`/api/profile`).
-   [ ] **Backend**: Implement the `firebase_auth.py` dependency to verify tokens.
-   [ ] **Frontend**: Create a basic Next.js app.
-   [ ] **Frontend**: Implement the Firebase SDK and `AuthProvider` to manage user login state.
-   [ ] **Frontend**: Create a simple login page and a profile page that calls the backend's protected endpoint.
-   [ ] **Local**: Create a `docker-compose.yml` file to run the backend and a local PostgreSQL database.

### Production Environment

-   [ ] **Production**: Create secrets in Google Secret Manager for `CREDENTIAL_ENCRYPTION_KEY` and `GOOGLE_APPLICATION_CREDENTIALS`.
-   [ ] **Production**: Add the Neon database connection string as a secret named `DATABASE_URL`.
-   [ ] **Production**: Configure Firebase Authentication in the console (e.g., enable Google Sign-In).
-   [ ] **Production**: Run the `scripts/deploy.sh` script for the first time.
-   [ ] **Verification**: Log in to the deployed production frontend and confirm that the profile page successfully fetches data from the backend.

---

## Phase 2: Database & Core Models

**Goal**: Establish the database schema and migration process.

### Local Environment

-   [ ] **Backend**: Define the SQLAlchemy models for `User` and `Credential` in `backend/app/models/database.py`.
-   [ ] **Backend**: Set up Alembic to manage database migrations.
-   [ ] **Backend**: Create an initial migration (`alembic revision --autogenerate`) to create the tables.
-   [ ] **Backend**: Run `alembic upgrade head` locally (via `docker-compose`) to apply the migration to the local database.

### Production Environment

-   [ ] **Backend**: Implement the `scripts/start.sh` script to run `alembic upgrade head` before the server starts.
-   [ ] **Backend**: Update the `Dockerfile` to use `scripts/start.sh` as its `CMD`.
-   [ ] **Production**: Deploy the updated application.
-   [ ] **Verification**: Check the Cloud Run logs to confirm the database migration ran successfully on startup.

---

## Phase 3: Service Authentication (OAuth Flows)

**Goal**: Allow users to securely connect their external service accounts.

### Local Environment

-   [ ] **Backend**: Implement the `encryption.py` service for encrypting/decrypting tokens.
-   [ ] **Backend**: Create API endpoints to initiate the OAuth flows for Outlook and Pipedrive (e.g., `/api/auth/connect/outlook`).
-   [ ] **Backend**: Create the callback endpoints (`/api/auth/callback/outlook`) to handle the response, exchange the code for tokens, encrypt them, and save them to the database.
-   [ ] **Frontend**: Build the UI components (e.g., "Connect" buttons) that link to the backend's OAuth initiation endpoints.

### Production Environment

-   [ ] **Production**: Update the redirect URIs in the Outlook and Pipedrive app configurations to point to the production Cloud Run service URL.
-   [ ] **Production**: Add the OAuth Client IDs and Secrets to Google Secret Manager.
-   [ ] **Production**: Deploy the updated application.
-   [ ] **Verification**: Go through the full connection flow on the production site for both Outlook and Pipedrive.

---

## Phase 4: Core Logic (Email to Deal)

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