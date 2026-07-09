from __future__ import annotations

import json
import logging
import time

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.notifications.models import NotificationJobPayload
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class NotificationRetryQueue:
    def __init__(self, repository: RedisRepository, settings: Settings, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()

    def _key(self) -> str:
        return self._keys.notifications_retry()

    def _delay_seconds(self, attempt: int) -> int:
        base = self._settings.NOTIFICATIONS_RETRY_BASE_DELAY_SECONDS
        return int(base * (2 ** max(0, attempt - 1)))

    async def schedule(self, payload: NotificationJobPayload, error: str) -> bool:
        if payload.attempt >= self._settings.NOTIFICATIONS_RETRY_MAX_ATTEMPTS:
            logger.error(
                "notification_retry_exhausted",
                extra={"job_id": payload.job_id, "error": error},
            )
            return False
        payload.attempt += 1
        run_at = time.time() + self._delay_seconds(payload.attempt)
        body = json.dumps({"payload": payload.model_dump(mode="json"), "error": error})
        ok = await self._repository.zadd(self._key(), {body: run_at})
        if ok:
            logger.info(
                "notification_retry_scheduled",
                extra={"job_id": payload.job_id, "attempt": payload.attempt, "run_at": run_at},
            )
        return ok

    async def poll_ready(self, limit: int = 10) -> list[NotificationJobPayload]:
        now = time.time()
        items = await self._repository.zrangebyscore(self._key(), 0, now, start=0, num=limit)
        payloads: list[NotificationJobPayload] = []
        for body in items:
            await self._repository.zrem(self._key(), body)
            try:
                data = json.loads(body)
                payloads.append(NotificationJobPayload.model_validate(data["payload"]))
            except Exception as exc:
                logger.warning("notification_retry_decode_failed", extra={"error": str(exc)})
        return payloads

    async def depth(self) -> int:
        return await self._repository.zcard(self._key())
