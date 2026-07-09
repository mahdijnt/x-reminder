from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.monitoring.models import JobRecord, JobType


class MonitoringStatusData(BaseModel):
    enabled: bool
    scheduler_running: bool
    worker_running: bool
    worker_in_flight: int
    queue_depth: int
    retry_queue_depth: int
    metrics: dict[str, int]


class MonitoringHealthData(BaseModel):
    status: str
    timestamp: datetime
    engine: dict[str, Any]
    last_successful_poll: dict[str, str | None]


class JobHistoryListData(BaseModel):
    items: list[JobRecord]


class TriggerJobRequest(BaseModel):
    app_user_id: str | None = None


class TriggerJobData(BaseModel):
    job_id: str
    job_type: JobType
    app_user_id: str
