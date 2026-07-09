from __future__ import annotations

import json
import logging

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.notifications.models import FailureRecord, NotificationJobPayload
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class NotificationFailureQueue:
    def __init__(self, repository: RedisRepository, settings: Settings, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()
        self._ttl = settings.NOTIFICATIONS_FAILURE_QUEUE_TTL_SECONDS

    def _list_key(self) -> str:
        return self._keys.notifications_failures()

    async def push(self, payload: NotificationJobPayload, error: str) -> bool:
        record = FailureRecord(payload=payload, error=error)
        body = record.model_dump(mode="json")
        raw = json.dumps(body)
        ok = await self._repository.rpush(self._list_key(), raw)
        detail_key = self._keys.notifications_failure_item(record.failure_id)
        await self._repository.set_json(detail_key, body, ex=self._ttl)
        if ok:
            logger.error(
                "notification_moved_to_failure_queue",
                extra={"job_id": payload.job_id, "failure_id": record.failure_id, "error": error},
            )
        return ok

    async def depth(self) -> int:
        return await self._repository.llen(self._list_key())
