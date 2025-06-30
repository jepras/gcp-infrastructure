# GCP Infrastructure Project

This project contains a backend API (FastAPI), a frontend application (Next.js), and uses PostgreSQL for its database.

## 1. Project Overview

This application is designed to process emails and integrate with various services. It consists of:

*   **Backend:** A FastAPI application (Python) handling API logic, authentication, and database interactions.
*   **Frontend:** A Next.js application (React/TypeScript) providing the user interface.
*   **Database:** PostgreSQL for data storage.

## 2. Getting Started Locally (Development)

Follow these steps to set up and run the application on your local machine for development.

### 2.1. Prerequisites

Before you begin, ensure you have the following installed:

*   **[Docker Desktop](https://www.docker.com/products/docker-desktop):** Required to run the local PostgreSQL database.
*   **Node.js and npm:** For the frontend development. (Recommended: Use `nvm` to manage Node.js versions).
*   **Python 3.9+ and pip:** For the backend development. (Recommended: Use `pyenv` or `conda` to manage Python versions).

### 2.2. Initial Setup (One-time)

Perform these steps once to set up your development environment.

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd gcp-infrastructure
    ```

2.  **Create and activate a Python virtual environment (for the backend):**
    From the **project root directory** (`gcp-infrastructure/`):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    (On Windows, use `venv\Scripts\activate`)

3.  **Install backend dependencies:**
    With the virtual environment activated, from the **project root directory**:
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Configure Environment Variables:**
    Copy `.env.example` to `.env` in the **project root directory** and fill in the required values. This includes your `DATABASE_URL` for local PostgreSQL and Firebase service account credentials.

5.  **Install frontend dependencies:**
    From the **project root directory**, navigate to the `frontend` directory and install dependencies:
    ```bash
    cd frontend
    npm install
    ```
    Then, navigate back to the **project root directory**:
    ```bash
    cd ..
    ```

### 2.3. Running the Application (Development)

To run the application, you will need to start the database, backend, and frontend. You can either start them individually in separate terminal windows/tabs, or use the `start_all.sh` script (macOS only).

#### Option A: Start Components Individually

Open three separate terminal windows/tabs, navigate to the **project root directory** (`gcp-infrastructure/`) in each, and run the following commands:

1.  **Start the Local Database:**
    Ensure Docker Desktop is running.
    ```bash
    docker compose up -d db
    ```
    This will start a PostgreSQL container accessible at `localhost:5433`.

2.  **Start the Backend:**
    ```bash
    ./scripts/start.sh
    ```
    The backend will be accessible at `http://localhost:8080`.

3.  **Start the Frontend:**
    ```bash
    ./scripts/start_frontend.sh
    ```
    The frontend will typically be accessible at `http://localhost:3000` (or another available port).

#### Option B: Start All Components (macOS only, experimental)

From the **project root directory**:

```bash
./scripts/start_all.sh
```

This script attempts to start the database, backend, and frontend in separate terminal windows. Check the new terminal windows for status and any errors.

## 3. Deployment (Production)

Deployment to Google Cloud Platform (Cloud Run for backend, Firebase Hosting for frontend) is handled by the `deploy.sh` script.

### 3.1. Prerequisites

*   **Google Cloud SDK (`gcloud` CLI):** Installed and authenticated to your GCP project.
*   **Firebase CLI:** Installed and authenticated to your Firebase project.
*   **Docker:** Installed and configured for your system.

### 3.2. Deployment Steps

From the **project root directory** (`gcp-infrastructure/`):

```bash
r ./scripts/deploy.sh
```

This script will:

1.  Build the backend Docker image.
2.  Push the image to Google Artifact Registry.
3.  Deploy the backend service to Google Cloud Run.
4.  Build the frontend application.
5.  Deploy the frontend to Firebase Hosting.

Ensure your `PROJECT_ID` and `FIREBASE_PROJECT_ID` are correctly set in `scripts/deploy.sh`.

### 3.3. Production URLs

Once deployed, your application will be accessible at the following URLs:

*   **Frontend (Firebase Hosting):** `https://gcp-infrastructure-464305.web.app`
*   **Backend (Cloud Run):** `https://ai-email-processor-backend-wa3fyyjtpq-uc.a.run.app`
