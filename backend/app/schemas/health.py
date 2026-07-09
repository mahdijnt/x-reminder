"""Health check response schemas."""

from datetime import datetime

from typing import Any

from pydantic import BaseModel, Field


class HealthCheckItem(BaseModel):
    status: str = Field(..., examples=["ok", "unavailable"])
    detail: str | None = None


class HealthData(BaseModel):
    status: str = Field(..., examples=["ok", "degraded"])
    version: str
    environment: str
    timestamp: datetime
    checks: dict[str, HealthCheckItem] = Field(default_factory=dict)


class RedisPoolStatus(BaseModel):
    status: str
    max_connections: int
    in_use: int = 0
    available: int = 0
    exhausted: bool = False


class RedisHealthData(BaseModel):
    connected: bool
    latency_ms: float | None = None
    pool: dict[str, Any] | RedisPoolStatus
    server_version: str | None = None
    detail: str | None = None
