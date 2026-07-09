from __future__ import annotations

import logging

from app.integrations.telegram.client import TelegramAPIError, TelegramClient
from app.notifications.message_builder import build_batch_message
from app.notifications.models import NotificationJobPayload
from app.notifications.rate_limiter import TelegramRateLimiter

logger = logging.getLogger(__name__)


class TelegramDelivery:
    def __init__(self, client: TelegramClient, rate_limiter: TelegramRateLimiter) -> None:
        self._client = client
        self._rate_limiter = rate_limiter

    async def deliver(self, payload: NotificationJobPayload) -> None:
        if not payload.tweets:
            raise TelegramAPIError("No tweets in notification payload")
        text = build_batch_message(payload.tweets)
        await self._rate_limiter.acquire(payload.telegram_id)
        await self._client.send_message(payload.telegram_id, text)
        logger.info(
            "notification_telegram_sent",
            extra={
                "job_id": payload.job_id,
                "app_user_id": payload.app_user_id,
                "telegram_id": payload.telegram_id,
                "tweet_count": len(payload.tweets),
            },
        )
