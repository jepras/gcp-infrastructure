from fastapi import FastAPI, Depends
from app.auth.firebase_auth import verify_token
from app.api.oauth import router as oauth_router
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(oauth_router, prefix="/api/auth")

@app.get("/api")
def read_root():
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to the AI Email Processor API"}


@app.get("/api/profile")
def get_profile(user: dict = Depends(verify_token)):
    logger.info(f"Profile endpoint accessed by user: {user.get('name', user.get('email', user.get('uid')))}")
    # The user object is the decoded Firebase token, which contains user info.
    return {"message": f"Hello, {user.get('name', 'user')}!", "user_id": user["uid"]}
