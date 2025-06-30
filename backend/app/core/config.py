import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    CREDENTIAL_ENCRYPTION_KEY: str
    GOOGLE_CLOUD_PROJECT: str
    OUTLOOK_CLIENT_ID: str
    OUTLOOK_CLIENT_SECRET: str
    PIPEDRIVE_CLIENT_ID: str
    PIPEDRIVE_CLIENT_SECRET: str


@lru_cache()
def get_settings():
    return Settings()
