from __future__ import annotations

from datetime import datetime, timezone

from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.repositories.redis_repository import RedisRepository


class LastPollStore:
    def __init__(self, repository: RedisRepository, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()

    async def get(self, app_user_id: str, list_type: str) -> datetime | None:
        raw = await self._repository.get(self._keys.monitoring_last_poll(app_user_id, list_type))
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw)
        except ValueError:
            return None

    async def set_now(self, app_user_id: str, list_type: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        return await self._repository.set(
            self._keys.monitoring_last_poll(app_user_id, list_type),
            now,
            ex=60 * 60 * 24 * 30,
        )
