from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application
    APP_NAME: str = "SmartRecruit API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    MAX_CV_FILE_SIZE_MB: int = 10

    # API
    API_PREFIX: str = ""

    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # MongoDB
    MONGODB_URI: str = "mongodb://mongodb:27017"
    MONGODB_DATABASE: str = "smart_recruit"

    # Qdrant
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "candidates"

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # SMTP / Email
    SMTP_HOST: str = "mailpit"
    SMTP_PORT: int = 1025
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = False
    SMTP_STARTTLS: bool = False
    EMAILS_FROM_EMAIL: str = "no-reply@smartrecruit.local"
    EMAILS_FROM_NAME: str = "SmartRecruit"

    # Email Verification
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 15
    VERIFICATION_MAX_ATTEMPTS: int = 5
    VERIFICATION_RESEND_COOLDOWN_SECONDS: int = 60

    # Neo4j
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = Field(default="")

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()