from __future__ import annotations

from datetime import datetime, timezone

from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.repositories.redis_repository import RedisRepository

_CURSOR_TTL_SECONDS = 60 * 60 * 24 * 90


def max_tweet_id(current: str | None, candidate: str | None) -> str | None:
    if not candidate:
        return current
    if not current:
        return candidate
    try:
        return candidate if int(candidate) > int(current) else current
    except ValueError:
        return candidate if candidate > current else current


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

    async def get_last_processed_tweet_id(
        self,
        app_user_id: str,
        list_type: str,
        x_user_id: str,
    ) -> str | None:
        raw = await self._repository.get(
            self._keys.monitoring_last_processed_tweet(app_user_id, list_type, x_user_id)
        )
        return raw or None

    async def set_last_processed_tweet_id(
        self,
        app_user_id: str,
        list_type: str,
        x_user_id: str,
        tweet_id: str,
    ) -> bool:
        if not tweet_id:
            return False
        key = self._keys.monitoring_last_processed_tweet(app_user_id, list_type, x_user_id)
        current = await self.get_last_processed_tweet_id(app_user_id, list_type, x_user_id)
        updated = max_tweet_id(current, tweet_id)
        if updated is None:
            return False
        return await self._repository.set(key, updated, ex=_CURSOR_TTL_SECONDS)
