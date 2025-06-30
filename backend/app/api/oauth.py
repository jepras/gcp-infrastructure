from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
import json
import logging
import urllib.parse
import secrets
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.database import get_db
from app.models.database import User, Credential
from app.auth.firebase_auth import verify_token
from app.services.encryption import encrypt_data

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

# In-memory session store for OAuth flows (in production, use Redis or database)
oauth_sessions = {}

# Outlook OAuth configuration
OUTLOOK_CLIENT_ID = settings.OUTLOOK_CLIENT_ID
OUTLOOK_CLIENT_SECRET = settings.OUTLOOK_CLIENT_SECRET
OUTLOOK_REDIRECT_URI = "http://localhost:8080/api/auth/callback/outlook"
OUTLOOK_SCOPES = "openid profile offline_access User.Read Mail.ReadWrite"
OUTLOOK_AUTHORIZE_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
OUTLOOK_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

# Pipedrive OAuth configuration
PIPEDRIVE_CLIENT_ID = settings.PIPEDRIVE_CLIENT_ID
PIPEDRIVE_CLIENT_SECRET = settings.PIPEDRIVE_CLIENT_SECRET
PIPEDRIVE_REDIRECT_URI = "http://localhost:8080/api/auth/callback/pipedrive"
PIPEDRIVE_SCOPES = "deals:full users:read"
PIPEDRIVE_AUTHORIZE_URL = "https://oauth.pipedrive.com/oauth/authorize"
PIPEDRIVE_TOKEN_URL = "https://oauth.pipedrive.com/oauth/token"


@router.post("/initiate/outlook")
async def initiate_outlook_oauth(user: dict = Depends(verify_token)):
    """Create a session and return the OAuth URL for Outlook."""
    if not OUTLOOK_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Outlook Client ID not configured",
        )

    # Create a session token
    session_token = secrets.token_urlsafe(32)
    oauth_sessions[session_token] = {
        "user_id": user["uid"],
        "service": "outlook",
        "created_at": "now",  # In production, use actual timestamp
    }

    # Include the session token in the state parameter
    state = f"{user['uid']}:{session_token}"

    auth_url = (
        f"{OUTLOOK_AUTHORIZE_URL}?"
        f"client_id={OUTLOOK_CLIENT_ID}&"
        f"response_type=code&"
        f"redirect_uri={OUTLOOK_REDIRECT_URI}&"
        f"scope={OUTLOOK_SCOPES}&"
        f"state={state}"
    )

    logger.info(
        f"Created OAuth session for user {user['uid']} with token: {session_token[:10]}..."
    )
    return {"auth_url": auth_url}


@router.get("/connect/outlook")
async def connect_outlook():
    """Legacy endpoint - redirects to initiate endpoint."""
    return RedirectResponse(url="/api/auth/initiate/outlook")


@router.get("/callback/outlook")
async def outlook_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Outlook OAuth callback. Extracts user ID from state parameter."""
    logger.info(
        f"Outlook callback received with code: {code[:10]}... and state: {state}"
    )

    if not OUTLOOK_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Outlook Client Secret not configured",
        )

    # Extract user ID and session token from state parameter
    try:
        firebase_uid, session_token = state.split(":", 1)
        logger.info(
            f"Extracted Firebase UID: {firebase_uid}, Session token: {session_token[:10]}..."
        )

        # Verify session
        if session_token not in oauth_sessions:
            logger.error(f"Invalid session token: {session_token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session"
            )

        session_data = oauth_sessions[session_token]
        if (
            session_data["user_id"] != firebase_uid
            or session_data["service"] != "outlook"
        ):
            logger.error(f"Session mismatch for token: {session_token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Session mismatch"
            )

        # Clean up session
        del oauth_sessions[session_token]

    except ValueError:
        logger.error(f"Invalid state parameter format: {state}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
        )

    token_data = {
        "client_id": OUTLOOK_CLIENT_ID,
        "client_secret": OUTLOOK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": OUTLOOK_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OUTLOOK_TOKEN_URL, data=token_data)
            response.raise_for_status()
            tokens = response.json()
            logger.info("Successfully exchanged authorization code for tokens")

        encrypted_access_token = encrypt_data(
            tokens["access_token"], settings.CREDENTIAL_ENCRYPTION_KEY
        )
        encrypted_refresh_token = encrypt_data(
            tokens["refresh_token"], settings.CREDENTIAL_ENCRYPTION_KEY
        )

        # Calculate expiration timestamp
        expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])

        # Find or create user in database
        db_user = db.query(User).filter(User.firebase_id == firebase_uid).first()
        if not db_user:
            logger.info(f"Creating new user for Firebase UID: {firebase_uid}")
            db_user = User(firebase_id=firebase_uid)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        else:
            logger.info(f"Found existing user for Firebase UID: {firebase_uid}")

        # Save or update credentials
        existing_credential = (
            db.query(Credential)
            .filter(
                Credential.user_id == db_user.id, Credential.service_name == "outlook"
            )
            .first()
        )

        if existing_credential:
            logger.info("Updating existing Outlook credentials")
            existing_credential.access_token = encrypted_access_token
            existing_credential.refresh_token = encrypted_refresh_token
            existing_credential.expires_at = expires_at
        else:
            logger.info("Creating new Outlook credentials")
            credential = Credential(
                user_id=db_user.id,
                service_name="outlook",
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                expires_at=expires_at,
            )
            db.add(credential)

        db.commit()
        logger.info("Outlook credentials saved successfully")

        return {"message": "Outlook connected successfully!"}

    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error during token exchange: {e.response.status_code} - {e.response.text}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {e.response.text}",
        )
    except Exception as e:
        logger.error(f"Error during Outlook OAuth callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.post("/initiate/pipedrive")
async def initiate_pipedrive_oauth(user: dict = Depends(verify_token)):
    """Create a session and return the OAuth URL for Pipedrive."""
    if not PIPEDRIVE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pipedrive Client ID not configured",
        )

    # Create a session token
    session_token = secrets.token_urlsafe(32)
    oauth_sessions[session_token] = {
        "user_id": user["uid"],
        "service": "pipedrive",
        "created_at": "now",  # In production, use actual timestamp
    }

    # Include the session token in the state parameter
    state = f"{user['uid']}:{session_token}"

    auth_url = (
        f"{PIPEDRIVE_AUTHORIZE_URL}?"
        f"client_id={PIPEDRIVE_CLIENT_ID}&"
        f"redirect_uri={PIPEDRIVE_REDIRECT_URI}&"
        f"scope={PIPEDRIVE_SCOPES}&"
        f"state={state}"
    )

    logger.info(
        f"Created OAuth session for user {user['uid']} with token: {session_token[:10]}..."
    )
    return {"auth_url": auth_url}


@router.get("/connect/pipedrive")
async def connect_pipedrive():
    """Legacy endpoint - redirects to initiate endpoint."""
    return RedirectResponse(url="/api/auth/initiate/pipedrive")


@router.get("/callback/pipedrive")
async def pipedrive_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Pipedrive OAuth callback. Extracts user ID from state parameter."""
    logger.info(
        f"Pipedrive callback received with code: {code[:10]}... and state: {state}"
    )

    if not PIPEDRIVE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pipedrive Client Secret not configured",
        )

    # Extract user ID and session token from state parameter
    try:
        firebase_uid, session_token = state.split(":", 1)
        logger.info(
            f"Extracted Firebase UID: {firebase_uid}, Session token: {session_token[:10]}..."
        )

        # Verify session
        if session_token not in oauth_sessions:
            logger.error(f"Invalid session token: {session_token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session"
            )

        session_data = oauth_sessions[session_token]
        if (
            session_data["user_id"] != firebase_uid
            or session_data["service"] != "pipedrive"
        ):
            logger.error(f"Session mismatch for token: {session_token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Session mismatch"
            )

        # Clean up session
        del oauth_sessions[session_token]

    except ValueError:
        logger.error(f"Invalid state parameter format: {state}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
        )

    token_data = {
        "client_id": PIPEDRIVE_CLIENT_ID,
        "client_secret": PIPEDRIVE_CLIENT_SECRET,
        "code": code,
        "redirect_uri": PIPEDRIVE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(PIPEDRIVE_TOKEN_URL, data=token_data)
            response.raise_for_status()
            tokens = response.json()
            logger.info("Successfully exchanged authorization code for tokens")

        encrypted_access_token = encrypt_data(
            tokens["access_token"], settings.CREDENTIAL_ENCRYPTION_KEY
        )
        encrypted_refresh_token = encrypt_data(
            tokens["refresh_token"], settings.CREDENTIAL_ENCRYPTION_KEY
        )

        # Calculate expiration timestamp
        expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])

        # Find or create user in database
        db_user = db.query(User).filter(User.firebase_id == firebase_uid).first()
        if not db_user:
            logger.info(f"Creating new user for Firebase UID: {firebase_uid}")
            db_user = User(firebase_id=firebase_uid)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        else:
            logger.info(f"Found existing user for Firebase UID: {firebase_uid}")

        # Save or update credentials
        existing_credential = (
            db.query(Credential)
            .filter(
                Credential.user_id == db_user.id, Credential.service_name == "pipedrive"
            )
            .first()
        )

        if existing_credential:
            logger.info("Updating existing Pipedrive credentials")
            existing_credential.access_token = encrypted_access_token
            existing_credential.refresh_token = encrypted_refresh_token
            existing_credential.expires_at = expires_at
        else:
            logger.info("Creating new Pipedrive credentials")
            credential = Credential(
                user_id=db_user.id,
                service_name="pipedrive",
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                expires_at=expires_at,
            )
            db.add(credential)

        db.commit()
        logger.info("Pipedrive credentials saved successfully")

        return {"message": "Pipedrive connected successfully!"}

    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error during token exchange: {e.response.status_code} - {e.response.text}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange authorization code: {e.response.text}",
        )
    except Exception as e:
        logger.error(f"Error during Pipedrive OAuth callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
