"""
Application configuration loaded from environment variables / .env file.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://finsense_user:finsense_pass@localhost:5432/finsense"

    # JWT
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ML
    HF_MODEL_NAME: str = "distilbert-base-uncased"

    # Environment
    ENVIRONMENT: str = "development"

    # CORS Allowed Origins (comma-separated list)
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
