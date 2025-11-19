from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Google / Gemini configuration
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_project_id: str = "YOUR_GCP_PROJECT_ID"
    google_location: str = "us-central1"

    # JWT Authentication
    jwt_secret: str = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this-in-production-min-32-chars")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = 60  # 1 hour
    refresh_token_expire_days: int = 7  # 7 days

    # File Upload Settings
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10
    allowed_file_types: list = [
        "image/jpeg", "image/png", "image/jpg",
        "application/pdf", "image/heic"
    ]
    
    # Database
    database_url: str = "sqlite:///./healthcare.db"
    
    # Security
    bcrypt_rounds: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "prescriptions"), exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "lab_results"), exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "documents"), exist_ok=True)