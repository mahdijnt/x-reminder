"""Health check response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class HealthData(BaseModel):
    status: str = Field(..., examples=["ok"])
    version: str
    environment: str
    timestamp: datetime
