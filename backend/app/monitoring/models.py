from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class JobType(str, Enum):
    POLL_FOLLOW_TARGETS = "poll_follow_targets"
    POLL_FOLLOWING = "poll_following"
    POLL_MUTUAL_FOLLOWERS = "poll_mutual_followers"
    SYNC_WATCH_LIST = "sync_watch_list"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class JobPayload(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    job_type: JobType
    app_user_id: str
    priority: int = 0
    attempt: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)
    enqueued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobRecord(BaseModel):
    job_id: str
    job_type: JobType
    status: JobStatus
    app_user_id: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    attempt: int = 1


class PollListType(str, Enum):
    FOLLOW_TARGETS = "follow-targets"
    FOLLOWING = "following"
    MUTUAL_FOLLOWERS = "mutual-followers"
