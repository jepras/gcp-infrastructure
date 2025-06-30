from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
import json

from app.core.config import get_settings
from app.core.database import get_db
from app.models.database import User, Credential
from app.auth.firebase_auth import verify_token
from app.services.encryption import encrypt_data

router = APIRouter()
settings = get_settings()

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

@router.get("/connect/outlook")
async def connect_outlook():
    if not OUTLOOK_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Outlook Client ID not configured")
    
    auth_url = (
        f"{OUTLOOK_AUTHORIZE_URL}?"
        f"client_id={OUTLOOK_CLIENT_ID}&"
        f"response_type=code&"
        f"redirect_uri={OUTLOOK_REDIRECT_URI}&"
        f"scope={OUTLOOK_SCOPES}"
    )
    return RedirectResponse(auth_url)

@router.get("/callback/outlook")
async def outlook_callback(code: str, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    if not OUTLOOK_CLIENT_SECRET:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Outlook Client Secret not configured")

    token_data = {
        "client_id": OUTLOOK_CLIENT_ID,
        "client_secret": OUTLOOK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": OUTLOOK_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OUTLOOK_TOKEN_URL, data=token_data)
        response.raise_for_status() # Raise an exception for HTTP errors
        tokens = response.json()

    encrypted_access_token = encrypt_data(tokens["access_token"], settings.CREDENTIAL_ENCRYPTION_KEY)
    encrypted_refresh_token = encrypt_data(tokens["refresh_token"], settings.CREDENTIAL_ENCRYPTION_KEY)

    # Save credentials to DB
    db_user = db.query(User).filter(User.firebase_id == user["uid"]).first()
    if not db_user:
        db_user = User(firebase_id=user["uid"], email=user["email"])
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    credential = Credential(
        user_id=db_user.id,
        service_name="outlook",
        access_token=encrypted_access_token,
        refresh_token=encrypted_refresh_token,
        expires_at=tokens["expires_in"], # This should be calculated from current time
        # Add other relevant fields like token_type, scope, etc.
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)

    return {"message": "Outlook connected successfully!"}

@router.get("/connect/pipedrive")
async def connect_pipedrive():
    if not PIPEDRIVE_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Pipedrive Client ID not configured")

    auth_url = (
        f"{PIPEDRIVE_AUTHORIZE_URL}?"
        f"client_id={PIPEDRIVE_CLIENT_ID}&"
        f"redirect_uri={PIPEDRIVE_REDIRECT_URI}&"
        f"scope={PIPEDRIVE_SCOPES}"
    )
    return RedirectResponse(auth_url)

@router.get("/callback/pipedrive")
async def pipedrive_callback(code: str, db: Session = Depends(get_db)):
    if not PIPEDRIVE_CLIENT_SECRET:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Pipedrive Client Secret not configured")

    token_data = {
        "client_id": PIPEDRIVE_CLIENT_ID,
        "client_secret": PIPEDRIVE_CLIENT_SECRET,
        "code": code,
        "redirect_uri": PIPEDRIVE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(PIPEDRIVE_TOKEN_URL, data=token_data)
        response.raise_for_status() # Raise an exception for HTTP errors
        tokens = response.json()

    encrypted_access_token = encrypt_data(tokens["access_token"], settings.CREDENTIAL_ENCRYPTION_KEY)
    encrypted_refresh_token = encrypt_data(tokens["refresh_token"], settings.CREDENTIAL_ENCRYPTION_KEY)

    # Save credentials to DB
    db_user = db.query(User).filter(User.firebase_id == user["uid"]).first()
    if not db_user:
        db_user = User(firebase_id=user["uid"], email=user["email"])
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    credential = Credential(
        user_id=db_user.id,
        service_name="pipedrive",
        access_token=encrypted_access_token,
        refresh_token=encrypted_refresh_token,
        expires_at=tokens["expires_in"], # This should be calculated from current time
        # Add other relevant fields like token_type, scope, etc.
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)

    return {"message": "Pipedrive connected successfully!"}