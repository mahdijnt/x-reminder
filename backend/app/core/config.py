"""Application configuration via Pydantic Settings."""

from enum import Enum
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Deployment environment identifiers."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "x-reminder-api"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False

    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = Field(default="change-me-in-production", min_length=8)

    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default_factory=lambda: ["*"])

    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = True
    REDIS_KEY_PREFIX: str = "xreminder"
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_SOCKET_TIMEOUT: float = 5.0
    REDIS_SOCKET_CONNECT_TIMEOUT: float = 5.0
    REDIS_HEALTH_CHECK_INTERVAL: int = 30
    REDIS_RETRY_MAX_ATTEMPTS: int = 3
    REDIS_RETRY_BASE_DELAY: float = 0.5
    REDIS_RETRY_MAX_DELAY: float = 10.0

    X_CLIENT_ID: str = ""
    X_CLIENT_SECRET: str = ""
    X_BEARER_TOKEN: str = ""
    X_API_KEY: str = ""
    X_API_SECRET: str = ""
    X_CALLBACK_URL: str = "http://localhost:8000/api/v1/x/oauth/callback"
    X_API_BASE_URL: str = "https://api.twitter.com"
    X_OAUTH_SCOPES: list[str] = Field(
        default_factory=lambda: ["tweet.read", "users.read", "follows.read", "offline.access"]
    )
    X_HTTP_TIMEOUT: float = 30.0
    X_RETRY_MAX_ATTEMPTS: int = 3
    X_RETRY_BASE_DELAY: float = 1.0
    X_RETRY_MAX_DELAY: float = 30.0
    X_SYNC_SCHEDULER_ENABLED: bool = False
    X_SYNC_INTERVAL_MINUTES: int = 30
    X_SYNC_APP_USER_IDS: list[str] = Field(default_factory=list)
    MONITORING_ENABLED: bool = False
    MONITORING_WORKER_ENABLED: bool = True
    MONITORING_SIX_HOUR_INTERVAL_MINUTES: int = 360
    MONITORING_REALTIME_INTERVAL_SECONDS: int = 120
    MONITORING_QUEUE_NAME: str = "monitoring:jobs"
    MONITORING_RETRY_MAX_ATTEMPTS: int = 5
    MONITORING_RETRY_BASE_DELAY_SECONDS: int = 30
    MONITORING_JOB_HISTORY_TTL_SECONDS: int = 604800
    MONITORING_WORKER_CONCURRENCY: int = 2
    MONITORING_SHUTDOWN_TIMEOUT_SECONDS: int = 30
    MONITORING_POLL_BATCH_SIZE: int = 50
    MONITORING_APP_USER_IDS: list[str] = Field(default_factory=list)


    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("X_OAUTH_SCOPES", mode="before")
    @classmethod
    def parse_x_oauth_scopes(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


    @field_validator("MONITORING_APP_USER_IDS", mode="before")
    @classmethod
    def parse_monitoring_users(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("X_SYNC_APP_USER_IDS", mode="before")
    @classmethod
    def parse_x_sync_users(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def x_oauth_configured(self) -> bool:
        return bool(self.X_CLIENT_ID and self.X_CLIENT_SECRET and self.X_CALLBACK_URL)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
