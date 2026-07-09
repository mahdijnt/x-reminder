from __future__ import annotations

import logging
import time

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.notifications.models import DeliveryHistoryRecord
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class DeliveryHistoryStore:
    def __init__(self, repository: RedisRepository, settings: Settings, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()
        self._ttl = settings.NOTIFICATIONS_HISTORY_TTL_SECONDS

    def _index_key(self) -> str:
        return self._keys.notifications_history_index()

    async def record(self, entry: DeliveryHistoryRecord) -> bool:
        key = self._keys.notifications_history(entry.notification_id)
        payload = entry.model_dump(mode="json")
        ok = await self._repository.set_json(key, payload, ex=self._ttl)
        score = entry.sent_at.timestamp()
        await self._repository.zadd(self._index_key(), {entry.notification_id: score})
        return ok

    async def list_recent(self, limit: int = 50) -> list[DeliveryHistoryRecord]:
        ids = await self._repository.zrevrange(self._index_key(), 0, max(0, limit - 1))
        records: list[DeliveryHistoryRecord] = []
        for nid in ids:
            payload = await self._repository.get_json(self._keys.notifications_history(nid))
            if not payload:
                continue
            try:
                records.append(DeliveryHistoryRecord.model_validate(payload))
            except Exception:
                continue
        return records

    async def summary(self) -> dict[str, int]:
        recent = await self.list_recent(limit=500)
        counts = {"sent": 0, "failed": 0, "skipped": 0, "pending": 0}
        for item in recent:
            counts[item.status.value] = counts.get(item.status.value, 0) + 1
        counts["total_recorded"] = len(recent)
        return counts
