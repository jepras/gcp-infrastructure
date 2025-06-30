import os
import logging
from functools import lru_cache

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

logger = logging.getLogger(__name__)

# Removed @lru_cache() as it was causing issues with environment variable changes
def get_firebase_app():
    # Check if the app is already initialized to prevent errors in hot-reload environments.
    if not firebase_admin._apps:
        logger.info(f"Initializing Firebase Admin SDK...")
        logger.info(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
        logger.info(f"GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")

        # In a production (Cloud Run) environment, GOOGLE_APPLICATION_CREDENTIALS
        # will be set to the path of the service account key file.
        # For local development, it can be set in the .env file.
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {'projectId': os.environ.get('GOOGLE_CLOUD_PROJECT')})
            logger.info("Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Firebase Admin SDK: {e}")
            raise
    return firebase_admin.get_app()

def verify_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    """
    Verifies a Firebase ID token and returns the decoded token (user payload).

    This function is a dependency that can be used in FastAPI endpoints to protect them.
    """
    if not token:
        logger.info("No token provided.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    try:
        logger.info(f"Attempting to verify token: {token[:30]}...") # Log first 30 chars of token
        # Ensure the Firebase app is initialized before trying to use it.
        get_firebase_app()
        decoded_token = auth.verify_id_token(token)
        logger.info(f"Token verified successfully for user: {decoded_token.get('uid')}")
        return decoded_token
    except auth.InvalidIdTokenError as e:
        logger.error(f"Invalid Firebase ID token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token"
        )
    except Exception as e:
        # Catch other potential Firebase errors
        logger.error(f"Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying token: {e}",
        )
