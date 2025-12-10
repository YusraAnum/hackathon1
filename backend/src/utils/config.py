from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database settings
    neon_db_url: Optional[str] = None

    # Vector database settings
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None

    # AI service settings
    openai_api_key: Optional[str] = None
    ai_model: str = "gpt-3.5-turbo"

    # Application settings
    app_name: str = "AI-Native Textbook API"
    debug: bool = False
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000

    # Security settings
    allow_origins: list = ["*"]

    # Performance settings
    max_concurrent_requests: int = 10
    request_timeout: int = 30

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "text"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


# Create a single instance of settings based on environment
def get_settings():
    env = os.getenv("ENVIRONMENT", "development")
    settings = Settings()
    if env.lower() == "production":
        settings.environment = "production"
        settings.debug = False
        settings.qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
        settings.allow_origins = [
            "https://your-domain.com",
            "https://www.your-domain.com"
        ]
        settings.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
        settings.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        settings.log_level = os.getenv("LOG_LEVEL", "INFO")
        settings.log_format = "json"
    else:
        settings.environment = "development"
        settings.debug = True
        settings.allow_origins = ["*"]
        settings.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
        settings.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        settings.log_level = os.getenv("LOG_LEVEL", "DEBUG")
        settings.log_format = "text"

    return settings


settings = get_settings()