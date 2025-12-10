from pydantic_settings import BaseSettings
from typing import Optional
import os


class ProductionSettings(BaseSettings):
    # Database settings
    neon_db_url: Optional[str] = os.getenv("NEON_DB_URL")

    # Vector database settings
    qdrant_url: str = os.getenv("QDRANT_URL", "http://qdrant:6333")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")

    # AI service settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    ai_model: str = os.getenv("AI_MODEL", "gpt-4")

    # Application settings
    app_name: str = "AI-Native Textbook API"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    environment: str = "production"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Security settings
    allow_origins: list = [
        "https://your-domain.com",
        "https://www.your-domain.com"
    ]

    # Performance settings
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # Logging settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "json"  # json for structured logging in production

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


class DevelopmentSettings(BaseSettings):
    # Database settings
    neon_db_url: Optional[str] = os.getenv("NEON_DB_URL")

    # Vector database settings
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")

    # AI service settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    ai_model: str = os.getenv("AI_MODEL", "gpt-3.5-turbo")

    # Application settings
    app_name: str = "AI-Native Textbook API"
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    environment: str = "development"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Security settings
    allow_origins: list = [
        "*"
    ]

    # Performance settings
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # Logging settings
    log_level: str = os.getenv("LOG_LEVEL", "DEBUG")
    log_format: str = "text"  # text for easier reading in development

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


# Create settings instance based on environment
def get_settings():
    env = os.getenv("ENVIRONMENT", "development")
    if env.lower() == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()


settings = get_settings()