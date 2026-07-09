"""Generate Sprint 13 notification system files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")
    print("wrote", rel)

w("app/integrations/telegram/__init__.py", '''
"""Telegram Bot API integration."""
from app.integrations.telegram.client import TelegramClient

__all__ = ["TelegramClient"]
''')

w("app/integrations/telegram/client.py", '''
"""Async HTTP client for Telegram Bot API."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"


class TelegramAPIError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, description: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.description = description


class TelegramClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "TelegramClient":
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _token(self) -> str:
        token = self._settings.TELEGRAM_BOT_TOKEN.strip()
        if not token:
            raise TelegramAPIError("TELEGRAM_BOT_TOKEN not configured", status_code=401)
        return token

    async def send_message(
        self,
        chat_id: str | int,
        text: str,
        *,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = False,
    ) -> dict[str, Any]:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        url = f"{TELEGRAM_API_BASE}/bot{self._token()}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        response = await self._client.post(url, json=payload)
        data = response.json()
        if response.status_code >= 400 or not data.get("ok"):
            description = None
            if isinstance(data.get("description"), str):
                description = data["description"]
            raise TelegramAPIError(
                description or f"Telegram API error HTTP {response.status_code}",
                status_code=response.status_code,
                description=description,
            )
        result = data.get("result")
        return result if isinstance(result, dict) else {}

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
''')

w("app/notifications/__init__.py", '''
from app.notifications.engine import NotificationEngine

__all__ = ["NotificationEngine"]
''')

w("app/notifications/models.py", '''
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
''')

print("part1 done")
