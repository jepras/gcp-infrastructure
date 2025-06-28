# Project Overview: AI Email Processor

This document outlines the architecture and development strategy for the AI Email Processor application. The goal is to build a secure, scalable, and cost-effective multi-tenant platform.

## 1. Core Architecture

The application is split into a modern frontend and a robust backend, deployed on a serverless-first stack to optimize for cost and scalability.

-   **Frontend**: A **Next.js** application deployed on **Firebase Hosting**. This provides a global CDN, automatic SSL, and seamless integration with our authentication provider.
-   **Backend**: A **Python FastAPI** application deployed as a container on **Google Cloud Run**. This allows the backend to scale from zero to handle any load, ensuring we only pay for what we use.
-   **Database**: A **Serverless PostgreSQL** provider with a generous free tier (e.g., Neon). This avoids the fixed monthly cost of Cloud SQL while maintaining full PostgreSQL compatibility.

![Architecture Diagram](https://storage.googleapis.com/gemini-assistant-images/project-architecture.png)

---

## 2. Authentication Strategy

Authentication is handled with a clear separation of concerns to maximize security and simplicity.

1.  **User Authentication**: Handled entirely by **Firebase Authentication**.
    -   The Next.js client uses the Firebase SDK for user sign-up and sign-in (e.g., with Google or email/password).
    -   Upon successful login, the client receives a JWT ID Token.
    -   This token is sent in the `Authorization` header of every API request to the backend.
    -   The FastAPI backend uses the Firebase Admin SDK to verify this token, securely identifying the user for every request.

2.  **Service Authorization**: Handled by the **FastAPI Backend**.
    -   When a user connects their Outlook or Pipedrive account, the backend manages the OAuth 2.0 flow.
    -   The resulting `access_token` and `refresh_token` are encrypted and stored in our PostgreSQL database, linked to the user's unique Firebase `user_id`.
    -   This ensures a strict separation of data and credentials between users (multi-tenancy).

---

## 3. Deployment & Environments

We maintain a clear distinction between local development and production environments, with a fully automated deployment process.

### Environments

-   **Local Development**:
    -   The full stack (backend, database) can be run locally using Docker and `docker-compose`.
    -   This provides a high-fidelity environment that mirrors production, minimizing environment-specific bugs.
    -   Uses local `.env` files for configuration.

-   **Production**:
    -   Deployed on Google Cloud Platform and Firebase.
    -   All secrets (API keys, database URLs) are stored securely in **Google Secret Manager**.
    -   The Cloud Run service is granted IAM permissions to access secrets at runtime.

### Deployment Process

A single shell script (`scripts/deploy.sh`) automates the entire deployment:

1.  The script reads the current Git commit hash to create a unique version tag.
2.  It builds the FastAPI application into a Docker container.
3.  It pushes the container image to **Google Artifact Registry**.
4.  It deploys the new container version to **Cloud Run**, securely injecting the latest secrets.
5.  It builds the Next.js frontend application.
6.  It deploys the frontend to **Firebase Hosting**.

Database migrations are handled by a startup script (`scripts/start.sh`) within the container, which runs `alembic upgrade head` before starting the web server. This ensures the database schema is always in sync with the application code.

---

## 4. Core Design Principles

-   **Security First**:
    -   Never store email content. Process in-memory and discard.
    -   Encrypt all sensitive credentials (service tokens, API keys) at rest.
    -   Rely on industry-standard authentication (Firebase, OAuth 2.0).

-   **Cost-Effective**:
    -   Use serverless technologies (Cloud Run, Neon, Firebase) to minimize fixed costs and benefit from generous free tiers.
    -   Implement strict usage limits on AI services to prevent unexpected bills.

-   **Developer Velocity**:
    -   Start with a well-structured monolith on Cloud Run for simplicity.
    -   Automate the entire deployment process to enable rapid, repeatable releases.
    -   Leverage managed services to reduce infrastructure overhead.

-   **Multi-Tenant by Design**:
    -   The architecture is built from the ground up to support multiple users signing up and securely connecting their own accounts. All data is partitioned by the user's unique ID.

---

## 5. Extensibility & Future Growth

The architecture is designed to be highly extensible, allowing for the easy addition of new services and AI capabilities without re-engineering the core system.

-   **Adding New Services (e.g., Slack, Trello)**: New third-party services can be integrated by replicating the existing OAuth and credential management pattern. A new service class can then be created and called from the core processing logic.

-   **Adding New AI Capabilities**: The use of a "Tool-Using" AI Agent (powered by LangChain) is a core architectural advantage.
    -   **New Tools**: We can grant the AI new abilities simply by writing standard Python functions (e.g., `search_google`, `check_calendar_availability`) and registering them as tools. The AI can then intelligently decide when to use them.
    -   **New Agents**: Entirely new AI agents with different goals (e.g., an agent for drafting email replies) can be developed and deployed as separate, modular components.

-   **Event-Driven Possibilities**: The system can be evolved to use a message queue (like Google Pub/Sub) to decouple processes. This would allow multiple, independent services to subscribe to events (like `deal_created`) and perform actions asynchronously, further enhancing modularity and reliability.

---

## 6. Project File Structure

The project is organized as a monorepo to keep the frontend and backend code in a single, manageable repository. The structure is designed for a clear separation of concerns.

```
ai-email-processor/
├── .env.example              # Example environment variables for local dev
├── .gitignore
├── Dockerfile                # Defines the container for the backend service
├── README.md
├── alembic.ini               # Alembic configuration for database migrations
├── requirements.txt          # Python dependencies for the backend
│
├── backend/                  # Python FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/              # API endpoint definitions (routers)
│   │   ├── auth/             # Authentication logic (Firebase, OAuth)
│   │   ├── core/             # Core components (DB session, config, encryption)
│   │   ├── models/           # Pydantic schemas and SQLAlchemy models
│   │   ├── services/         # Business logic (EmailProcessor, PipedriveService)
│   │   └── utils/            # Shared utilities (logging, etc.)
│   ├── main.py               # FastAPI application entry point
│   └── tests/                # Backend tests
│
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/              # Next.js App Router pages and layouts
│   │   ├── components/       # Reusable React components (UI, forms)
│   │   ├── lib/              # Core frontend logic (API client, auth, hooks)
│   │   └── styles/           # Global styles
│   ├── public/               # Static assets
│   ├── next.config.js
│   └── package.json
│
├── docs/                     # Project documentation
│   ├── project_overview.md
│   └── coding_standards.md
│
├── migrations/               # Alembic-generated database migration scripts
│
└── scripts/                  # Deployment and operational scripts
    ├── deploy.sh
    └── start.sh
```