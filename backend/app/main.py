from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.auth.firebase_auth import verify_token
from app.api.oauth import router as oauth_router
from app.core.database import get_db
from app.models.database import User, Credential
from app.services.encryption import decrypt_data
from app.core.config import get_settings
from sqlalchemy.orm import Session
import httpx
import logging
import os
import traceback

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(
    f"App starting. GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}"
)
logger.info(
    f"App starting. GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT')}"
)

app = FastAPI()

# Enable CORS for all origins (for local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(oauth_router, prefix="/api/auth")


@app.get("/api")
def read_root():
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to the AI Email Processor API"}


@app.get("/api/test")
def test_endpoint():
    logger.info("Test endpoint accessed - backend is working!")
    return {"message": "Backend test endpoint working!", "status": "success"}


@app.get("/api/test-pipedrive")
async def test_pipedrive(
    user: dict = Depends(verify_token), db: Session = Depends(get_db)
):
    """Test Pipedrive API connectivity using stored credentials."""
    try:
        logger.info(
            f"Testing Pipedrive API for user: {user.get('name', user.get('email', user.get('uid')))}"
        )

        # Find user and their Pipedrive credentials
        db_user = db.query(User).filter(User.firebase_id == user["uid"]).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        credential = (
            db.query(Credential)
            .filter(
                Credential.user_id == db_user.id, Credential.service_name == "pipedrive"
            )
            .first()
        )

        if not credential:
            raise HTTPException(
                status_code=404, detail="Pipedrive credentials not found"
            )

        # Decrypt the access token
        access_token = decrypt_data(
            credential.access_token, get_settings().CREDENTIAL_ENCRYPTION_KEY
        )

        # Test Pipedrive API by fetching user info
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.pipedrive.com/v1/users/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                user_data = response.json()
                logger.info("Successfully connected to Pipedrive API")
                return {
                    "message": "Pipedrive API test successful!",
                    "pipedrive_user": {
                        "name": user_data.get("data", {}).get("name"),
                        "email": user_data.get("data", {}).get("email"),
                        "company": user_data.get("data", {}).get("company_name"),
                    },
                }
            else:
                logger.error(
                    f"Pipedrive API error: {response.status_code} - {response.text}"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Pipedrive API error: {response.status_code}",
                )

    except Exception as e:
        logger.error(f"Error testing Pipedrive API: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Error testing Pipedrive API: {str(e)}"
        )


@app.get("/api/profile")
def get_profile(user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    try:
        logger.info(
            f"Profile endpoint accessed by user: {user.get('name', user.get('email', user.get('uid')))}"
        )
        logger.info(f"Full user object: {user}")

        # Find or create user in database and update email if available
        db_user = db.query(User).filter(User.firebase_id == user["uid"]).first()
        if not db_user:
            logger.info(f"Creating new user for Firebase UID: {user['uid']}")
            db_user = User(firebase_id=user["uid"], email=user.get("email"))
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        elif user.get("email") and db_user.email != user.get("email"):
            # Update email if it has changed
            logger.info(
                f"Updating email for user {user['uid']}: {db_user.email} -> {user.get('email')}"
            )
            db_user.email = user.get("email")
            db.commit()

        # The user object is the decoded Firebase token, which contains user info.
        return {
            "message": f"Hello, {user.get('name', 'user')}!",
            "user_id": user["uid"],
        }
    except Exception as e:
        logger.error(f"Error in profile endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
