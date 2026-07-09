"""Cached X profile payloads per app user."""

from __future__ import annotations

from app.infrastructure.redis.keys import RedisKeys, RedisTTL, get_redis_keys
from app.models.x.user import XProfile
from app.repositories.redis_repository import RedisRepository


class XProfileRepository:
    def __init__(self, repository: RedisRepository, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()

    async def get_profile(self, app_user_id: str) -> XProfile | None:
        payload = await self._repository.get_json(self._keys.x_profile(app_user_id))
        if not payload:
            return None
        return XProfile.model_validate(payload)

    async def save_profile(self, app_user_id: str, profile: XProfile) -> bool:
        return await self._repository.set_json(
            self._keys.x_profile(app_user_id),
            profile.model_dump(mode="json"),
            ex=RedisTTL.CACHE_LONG,
        )

    async def set_last_scan(self, app_user_id: str, timestamp: int) -> bool:
        return await self._repository.set(
            self._keys.x_last_scan(app_user_id),
            str(timestamp),
            ex=RedisTTL.CACHE_LONG * 7,
        )

    async def get_last_scan(self, app_user_id: str) -> int | None:
        raw = await self._repository.get(self._keys.x_last_scan(app_user_id))
        if raw is None:
            return None
        try:
            return int(raw)
        except ValueError:
            return None
