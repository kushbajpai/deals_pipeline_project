"""Core configuration management for the application."""

import logging
from functools import lru_cache
from typing import Any, Dict

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Uses pydantic-settings for environment variable management with
    support for .env files.
    """

    # Application
    app_name: str = "Deals Processor API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # Logging
    log_level: str = "INFO"

    # Authentication
    jwt_secret_key: str = (
        "your-secret-key-change-in-production-minimum-32-characters"
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # Password
    password_min_length: int = 8
    bcrypt_rounds: int = 12

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class LogConfig(Dict[str, Any]):
    """Logging configuration dictionary."""

    def __init__(self) -> None:
        """Initialize logging configuration."""
        self.config: Dict[str, Any] = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "detailed": {
                    "format": (
                        "%(asctime)s - %(name)s - %(levelname)s - "
                        "%(filename)s:%(lineno)d - %(message)s"
                    ),
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "detailed": {
                    "formatter": "detailed",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "deals_processor": {
                    "handlers": ["detailed"],
                    "level": "DEBUG",
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }

    def __getitem__(self, key: str) -> Any:
        """Get item from config."""
        return self.config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item in config."""
        self.config[key] = value


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Application settings instance.
    """
    return Settings()


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for module.

    Args:
        name: Logger name, typically __name__.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
