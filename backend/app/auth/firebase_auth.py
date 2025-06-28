import os
from functools import lru_cache

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


@lru_cache()
def get_firebase_app():
    # Check if the app is already initialized to prevent errors in hot-reload environments.
    if not firebase_admin._apps:
        # In a production (Cloud Run) environment, GOOGLE_APPLICATION_CREDENTIALS
        # will be set to the path of the service account key file.
        # For local development, it can be set in the .env file.
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    return firebase_admin.get_app()

def verify_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    """
    Verifies a Firebase ID token and returns the decoded token (user payload).

    This function is a dependency that can be used in FastAPI endpoints to protect them.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    try:
        # Ensure the Firebase app is initialized before trying to use it.
        get_firebase_app()
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token"
        )
    except Exception as e:
        # Catch other potential Firebase errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying token: {e}",
        )
