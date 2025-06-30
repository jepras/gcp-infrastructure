# Authentication & Authorization Strategy

This document details the authentication and authorization mechanisms implemented in the AI Email Processor application. A secure and robust strategy is crucial for a multi-tenant platform handling sensitive user data and external service integrations.

## 1. User Authentication (Firebase Authentication)

User authentication is handled entirely by **Firebase Authentication**. This provides a secure, scalable, and easy-to-implement solution for user sign-up and sign-in.

### 1.1. Flow

1.  **Frontend (Next.js)**:
    *   The Next.js client uses the Firebase SDK (e.g., `firebase/auth`) to manage user sign-up and sign-in. This can include various methods like Google Sign-In, email/password, etc.
    *   Upon successful authentication (e.g., a user logs in with their Google account), the Firebase SDK provides a JSON Web Token (JWT) called an **ID Token**.

2.  **Backend (FastAPI)**:
    *   For every API request that requires user authentication (i.e., protected endpoints), the frontend sends this Firebase ID Token in the `Authorization` header as a Bearer token (e.g., `Authorization: Bearer <ID_TOKEN>`).
    *   The FastAPI backend uses the **Firebase Admin SDK** to verify the authenticity and validity of this ID Token.
    *   The `verify_token` dependency (in `backend/app/auth/firebase_auth.py`) performs this verification. It decodes the token and extracts the user's unique Firebase `uid` (User ID) and other claims (like email, name).
    *   If the token is valid, the decoded user information is injected into the FastAPI endpoint's dependencies, allowing the backend to securely identify the user making the request.
    *   If the token is invalid or missing, the backend returns a `401 Unauthorized` error.

### 1.2. Tokens Stored (User Authentication)

*   **Frontend**: The Firebase SDK manages the user's session and stores the ID Token (and potentially refresh tokens) securely in the browser's local storage or session storage. These are handled by the Firebase SDK itself and are not directly managed by our application code.
*   **Backend**: The backend does **not** store the Firebase ID Tokens. It only verifies them on a per-request basis. The user's `firebase_id` (UID) and `email` are stored in the `users` table in the PostgreSQL database upon their first interaction with a protected endpoint (e.g., when they first access their profile or connect an external service).

## 2. Service Authorization (OAuth 2.0)

Authorization to external services (like Outlook and Pipedrive) is handled via **OAuth 2.0**. The backend manages the OAuth flow and securely stores the resulting access and refresh tokens.

### 2.1. Flow

1.  **Initiation (Frontend to Backend)**:
    *   When a user wants to connect an external service (e.g., Outlook), the frontend redirects the user's browser to a backend endpoint (e.g., `/api/auth/connect/outlook`).
    *   This backend endpoint (in `backend/app/api/oauth.py`) constructs the OAuth provider's authorization URL, including the `client_id`, `redirect_uri`, and requested `scopes`.
    *   The backend then redirects the user's browser to this OAuth provider's authorization URL.

2.  **User Consent (OAuth Provider)**:
    *   The user logs into the OAuth provider (e.g., Microsoft for Outlook, Pipedrive) and grants permission for our application to access their data.

3.  **Callback (OAuth Provider to Backend)**:
    *   After the user grants consent, the OAuth provider redirects the user's browser back to a pre-configured **callback URI** on our backend (e.g., `http://localhost:8080/api/auth/callback/outlook`). This redirect includes an authorization `code`.
    *   The backend's callback endpoint receives this `code`.

4.  **Token Exchange (Backend to OAuth Provider)**:
    *   The backend makes a server-to-server HTTP POST request to the OAuth provider's **token endpoint**. This request includes the `client_id`, `client_secret`, the received `code`, and the `redirect_uri`.
    *   The OAuth provider validates this request and, if successful, returns an `access_token` and often a `refresh_token`.

5.  **Credential Storage (Backend to Database)**:
    *   The `access_token` and `refresh_token` (if provided) are **encrypted** using a symmetric encryption key (`CREDENTIAL_ENCRYPTION_KEY`) managed by the backend.
    *   These encrypted tokens, along with their expiration time and the service name, are stored in the `credentials` table in the PostgreSQL database. Each credential entry is linked to the user's `id` (from the `users` table).

### 2.2. Tokens Stored (Service Authorization)

*   **Backend (Database)**: The `access_token` and `refresh_token` obtained from external OAuth providers are stored in the `credentials` table in the PostgreSQL database. **Crucially, these tokens are always stored in an encrypted format at rest.**
*   **Encryption Key**: The `CREDENTIAL_ENCRYPTION_KEY` used for encryption/decryption is loaded from environment variables (local development) or Google Secret Manager (production) and is never hardcoded or committed to the repository.

### 2.3. Using Stored Credentials

*   When the backend needs to interact with an external service on behalf of a user (e.g., fetch emails from Outlook, create a deal in Pipedrive), it retrieves the encrypted `access_token` (and `refresh_token` if needed) from the database.
*   It then **decrypts** the token(s) using the `CREDENTIAL_ENCRYPTION_KEY`.
*   The decrypted `access_token` is used to make API calls to the external service.
*   If an `access_token` expires, the `refresh_token` is used to obtain a new `access_token` without requiring the user to re-authenticate with the OAuth provider.

## 3. Security Considerations

*   **Separation of Concerns**: Firebase handles user authentication, while the backend handles service authorization. This minimizes the attack surface.
*   **Encryption at Rest**: All sensitive external service credentials are encrypted when stored in the database.
*   **Environment Variables/Secret Manager**: Sensitive keys and secrets are never hardcoded and are managed securely.
*   **Token Verification**: Firebase ID Tokens are rigorously verified by the backend to ensure authenticity and prevent unauthorized access.
*   **Least Privilege**: Services and roles are granted only the minimum permissions necessary.
