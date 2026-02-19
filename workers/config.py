"""Worker configuration."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Worker settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # MongoDB
    mongodb_url: str = Field(
        default="mongodb://infrawatch:infrawatch123@localhost:27017/infrawatch?authSource=admin"
    )
    mongodb_db_name: str = "infrawatch"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # RabbitMQ (alternative broker)
    rabbitmq_url: str = "amqp://infrawatch:infrawatch123@localhost:5672/"

    # Notifications
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook_url: str = ""

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""

    # Worker settings
    worker_concurrency: int = 4
    task_timeout: int = 300


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
