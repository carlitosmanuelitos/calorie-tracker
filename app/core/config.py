from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
from pathlib import Path

class Settings(BaseSettings):
    """Application settings."""
    # Base
    PROJECT_NAME: str = "Calorie Tracker"
    
    # Authentication
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./sql_app.db"
    DB_ECHO_LOG: bool = True

    # First superuser
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123!@#A"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()
