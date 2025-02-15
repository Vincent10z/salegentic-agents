# app/core/config.py
from functools import lru_cache
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import validator
import json
import logging
import logging.config


class Settings(BaseSettings):
    # App Settings
    APP_ENV: str
    DEBUG: bool
    APP_HOST: str
    APP_PORT: int

    # Database
    DATABASE_URL: str

    # HubSpot
    HUBSPOT_CLIENT_ID: str
    HUBSPOT_CLIENT_SECRET: str
    HUBSPOT_BASE_URL: str
    HUBSPOT_REDIRECT_URI: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Vector Store
    VECTOR_DB_HOST: str
    VECTOR_DB_PORT: int
    VECTOR_DB_COLLECTION: str

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None

    # Redis
    REDIS_URL: str

    # Logging
    LOG_LEVEL: str
    LOG_FORMAT: str

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql+asyncpg://", "postgresql://")):
            raise ValueError("Database URL must be a PostgreSQL connection string")
        return v

    @validator("LOG_FORMAT")
    def validate_log_format(cls, v: str) -> str:
        if v not in ["json", "text"]:
            raise ValueError("Log format must be either 'json' or 'text'")
        return v

    def get_logging_config(self) -> Dict[str, Any]:
        """Generate logging configuration based on settings."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
                },
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "formatter": "json" if self.LOG_FORMAT == "json" else "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout"
                }
            },
            "root": {
                "handlers": ["default"],
                "level": self.LOG_LEVEL
            }
        }

    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging_config = self.get_logging_config()
        logging.config.dictConfig(logging_config)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.setup_logging()
    return settings


# Create a global settings instance
settings = get_settings()

# Initialize logging
logger = logging.getLogger(__name__)
