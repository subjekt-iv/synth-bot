from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str

    # Qdrant Vector Database
    qdrant_api_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None

    # PostgreSQL Database
    database_url: str

    # Application Settings
    app_name: str = "Synthesizer Chatbot API"
    debug: bool = True
    log_level: str = "INFO"

    # File Upload Settings
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Global settings instance
settings = Settings()  # type: ignore[call-arg]

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
