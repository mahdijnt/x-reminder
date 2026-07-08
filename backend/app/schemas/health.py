"""Health check response schemas."""

from datetime import datetime

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
