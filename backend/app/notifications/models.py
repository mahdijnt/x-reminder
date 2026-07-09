from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class NotificationPriority(str, Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DeliveryChannel(str, Enum):
    TELEGRAM = "telegram"


class DeliveryStatus(str, Enum):
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING = "pending"


class TweetNotificationData(BaseModel):
    tweet_id: str
    author_id: str
    username: str
    url: str
    created_at: datetime
    list_type: str = "following"


class NotificationJobPayload(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    app_user_id: str
    telegram_id: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    attempt: int = 1
    tweets: list[TweetNotificationData] = Field(default_factory=list)
    enqueued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeliveryHistoryRecord(BaseModel):
    notification_id: str
    app_user_id: str
    tweet_id: str
    channel: DeliveryChannel = DeliveryChannel.TELEGRAM
    status: DeliveryStatus
    sent_at: datetime
    error: str | None = None
    telegram_id: str | None = None


class FailureRecord(BaseModel):
    failure_id: str = Field(default_factory=lambda: str(uuid4()))
    payload: NotificationJobPayload
    error: str
    failed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
