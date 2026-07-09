from __future__ import annotations

import json
import logging

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.monitoring.models import JobPayload
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class QueueManager:
    def __init__(self, repository: RedisRepository, settings: Settings, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()

    def _queue_key(self, priority: bool = False) -> str:
        parts = self._settings.MONITORING_QUEUE_NAME.split(":")
        base = self._keys._key(*parts)
        if priority:
            return f"{base}:priority"
        return base

    async def enqueue(self, payload: JobPayload) -> bool:
        data = payload.model_dump(mode="json")
        body = json.dumps(data)
        use_priority = payload.priority > 0
        ok = await self._repository.rpush(self._queue_key(use_priority), body)
        if ok:
            logger.info(
                "monitoring_job_enqueued",
                extra={
                    "job_id": payload.job_id,
                    "job_type": payload.job_type.value,
                    "app_user_id": payload.app_user_id,
                    "priority": payload.priority,
                },
            )
        return ok

    async def dequeue(self) -> JobPayload | None:
        for priority in (True, False):
            raw = await self._repository.lpop(self._queue_key(priority))
            if raw:
                try:
                    return JobPayload.model_validate_json(raw)
                except Exception as exc:
                    logger.warning("monitoring_job_decode_failed", extra={"error": str(exc)})
        return None

    async def depth(self) -> int:
        return (await self._repository.llen(self._queue_key(True))) + (
            await self._repository.llen(self._queue_key(False))
        )
