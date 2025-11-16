from pydantic import BaseSettings


class Settings(BaseSettings):
    # Google / Gemini configuration (ADK uses environment or ADC)
    google_project_id: str = "YOUR_GCP_PROJECT_ID"
    google_location: str = "us-central1"

    # App secrets
    jwt_secret: str = "HEALTHCARE_MULTI_AGENT_SECRET"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
