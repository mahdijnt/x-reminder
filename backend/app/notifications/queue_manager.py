from __future__ import annotations

import json
import logging

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.notifications.models import NotificationJobPayload, NotificationPriority
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)

_PRIORITY_ORDER = (
    NotificationPriority.HIGH,
    NotificationPriority.NORMAL,
    NotificationPriority.LOW,
)


class NotificationQueueManager:
    def __init__(self, repository: RedisRepository, settings: Settings, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()

    def _queue_key(self, priority: NotificationPriority) -> str:
        parts = self._settings.NOTIFICATIONS_QUEUE_NAME.split(":")
        base = self._keys._key(*parts)
        if priority == NotificationPriority.HIGH:
            return self._keys.notifications_queue_priority("high")
        if priority == NotificationPriority.LOW:
            return f"{base}:low"
        return base

    async def enqueue(self, payload: NotificationJobPayload) -> bool:
        body = payload.model_dump(mode="json")
        raw = json.dumps(body)
        ok = await self._repository.rpush(self._queue_key(payload.priority), raw)
        if ok:
            logger.info(
                "notification_job_enqueued",
                extra={
                    "job_id": payload.job_id,
                    "app_user_id": payload.app_user_id,
                    "priority": payload.priority.value,
                    "tweet_count": len(payload.tweets),
                },
            )
        return ok

    async def dequeue(self) -> NotificationJobPayload | None:
        for priority in _PRIORITY_ORDER:
            raw = await self._repository.lpop(self._queue_key(priority))
            if raw:
                try:
                    return NotificationJobPayload.model_validate_json(raw)
                except Exception as exc:
                    logger.warning("notification_job_decode_failed", extra={"error": str(exc)})
        return None

    async def depth(self) -> dict[str, int]:
        depths: dict[str, int] = {}
        total = 0
        for priority in _PRIORITY_ORDER:
            n = await self._repository.llen(self._queue_key(priority))
            depths[priority.value] = n
            total += n
        depths["total"] = total
        return depths
