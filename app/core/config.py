# app/core/config.py
import os
from functools import lru_cache
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import validator
import json
import logging
import logging.config


class Settings(BaseSettings):
    # App Settings
    APP_ENV: Optional[str] = None
    DEBUG: Optional[bool] = None

    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "postgres"

    PROJECT_NAME: Optional[str] = None
    PROJECT_DESCRIPTION: Optional[str] = None
    APP_VERSION: Optional[str] = None
    API_VERSION: Optional[str] = None

    # Database
    DATABASE_URL: Optional[str] = None

    # HubSpot
    HUBSPOT_CLIENT_ID: Optional[str] = None
    HUBSPOT_CLIENT_SECRET: Optional[str] = None
    HUBSPOT_APP_ID: Optional[str] = None
    HUBSPOT_BASE_URL: Optional[str] = None
    HUBSPOT_REDIRECT_URI: Optional[str] = None

    # JWT
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None

    # Vector Store
    VECTOR_DB_HOST: Optional[str] = None
    VECTOR_DB_PORT: Optional[int] = None
    VECTOR_DB_COLLECTION: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None

    # Redis
    REDIS_URL: Optional[str] = None

    # Logging
    LOG_LEVEL: Optional[str] = None
    LOG_FORMAT: Optional[str] = None

    @property
    def RETURN_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # @validator("DATABASE_URL")
    # def validate_database_url(cls, v: str) -> str:
    #     if not v.startswith(("postgresql+asyncpg://", "postgresql://")):
    #         raise ValueError("Database URL must be a PostgreSQL connection string")
    #     return v
    #
    # @validator("LOG_FORMAT")
    # def validate_log_format(cls, v: str) -> str:
    #     if v not in ["json", "text"]:
    #         raise ValueError("Log format must be either 'json' or 'text'")
    #     return v
    #
    # def get_logging_config(self) -> Dict[str, Any]:
    #     """Generate logging configuration based on settings."""
    #     return {
    #         "version": 1,
    #         "disable_existing_loggers": False,
    #         "formatters": {
    #             "json": {
    #                 "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
    #                 "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
    #             },
    #             "standard": {
    #                 "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    #             }
    #         },
    #         "handlers": {
    #             "default": {
    #                 "formatter": "json" if self.LOG_FORMAT == "json" else "standard",
    #                 "class": "logging.StreamHandler",
    #                 "stream": "ext://sys.stdout"
    #             }
    #         },
    #         "root": {
    #             "handlers": ["default"],
    #             "level": self.LOG_LEVEL
    #         }
    #     }
    #
    # def setup_logging(self) -> None:
    #     """Configure logging based on settings."""
    #     logging_config = self.get_logging_config()
    #     logging.config.dictConfig(logging_config)
    #

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    print("DEBUG: Environment variables loaded:")
    print(f"HUBSPOT_CLIENT_ID: {settings.HUBSPOT_CLIENT_ID}")
    print(f"HUBSPOT_APP_ID: {settings.HUBSPOT_APP_ID}")
    print(f"HUBSPOT_CLIENT_SECRET: {settings.HUBSPOT_CLIENT_SECRET}")
    print(f"HUBSPOT_REDIRECT_URI: {settings.HUBSPOT_REDIRECT_URI}")
    return settings


# Create a global settings instance
settings = get_settings()

# Initialize logging
# logger = logging.getLogger(__name__)
