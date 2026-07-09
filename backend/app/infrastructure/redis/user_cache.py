"""Placeholder user data cache (no authentication flow)."""

from __future__ import annotations

import logging
from typing import Any

from app.infrastructure.redis.keys import RedisKeys, get_redis_keys, get_redis_ttl
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class UserCache:
    """Cache interface for user profile blobs keyed by user_id."""

    def __init__(
        self,
        repository: RedisRepository,
        keys: RedisKeys | None = None,
        default_ttl: int | None = None,
    ) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()
        self._default_ttl = default_ttl if default_ttl is not None else get_redis_ttl().user_cache

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        payload = await self._repository.get_json(self._keys.user(user_id))
        if isinstance(payload, dict):
            return payload
        return None

    async def set_user(
        self,
        user_id: str,
        data: dict[str, Any],
        *,
        ttl: int | None = None,
    ) -> bool:
        return await self._repository.set_json(
            self._keys.user(user_id),
            data,
            ex=ttl if ttl is not None else self._default_ttl,
        )

    async def invalidate(self, user_id: str) -> int:
        return await self._repository.delete(self._keys.user(user_id))
