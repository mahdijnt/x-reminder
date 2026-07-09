from __future__ import annotations

import logging

from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)

METRIC_KEYS = (
    "notifications_sent",
    "notifications_failed",
    "notifications_skipped",
    "notification_retries",
    "queue_depth",
)


class NotificationMetrics:
    def __init__(self, repository: RedisRepository, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()
        self._local: dict[str, int] = {k: 0 for k in METRIC_KEYS}

    def _hash_key(self) -> str:
        return self._keys.notifications_metrics()

    async def incr(self, name: str, amount: int = 1) -> None:
        if name in self._local:
            self._local[name] += amount
        await self._repository.hincrby(self._hash_key(), name, amount)

    async def set_gauge(self, name: str, value: int) -> None:
        self._local[name] = value
        await self._repository.hset(self._hash_key(), name, str(value))

    async def snapshot(self) -> dict[str, int]:
        raw = await self._repository.hgetall(self._hash_key())
        merged = dict(self._local)
        for k, v in raw.items():
            try:
                merged[k] = int(v)
            except ValueError:
                continue
        return merged

    def prometheus_text(self, data: dict[str, int]) -> str:
        lines = []
        for key, value in sorted(data.items()):
            lines.append(f"notification_{key} {value}")
        return "\n".join(lines) + "\n"
