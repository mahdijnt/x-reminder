from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.notifications.models import DeliveryHistoryRecord


class NotificationStatusData(BaseModel):
    enabled: bool
    worker_enabled: bool
    worker_running: bool
    worker_in_flight: int
    queue_depth: dict[str, int]
    retry_queue_depth: int
    failure_queue_depth: int
    metrics: dict[str, int]
    telegram_configured: bool


class NotificationHistoryData(BaseModel):
    items: list[DeliveryHistoryRecord]


class NotificationReportsData(BaseModel):
    delivery_summary: dict[str, int]
    metrics: dict[str, int]
    queue_depth: dict[str, int]


class NotificationTestRequest(BaseModel):
    telegram_id: str
    message: str | None = None


class NotificationTriggerRequest(BaseModel):
    app_user_id: str | None = None
    limit: int = Field(default=50, ge=1, le=500)
