"""Application-level cache with TTL and namespacing."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.infrastructure.redis.keys import RedisKeys, RedisTTL, get_redis_keys
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class CacheService:
    """High-level cache for arbitrary application data."""

    def __init__(
        self,
        repository: RedisRepository,
        keys: RedisKeys | None = None,
        default_ttl: int = RedisTTL.CACHE_DEFAULT,
    ) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()
        self._default_ttl = default_ttl

    def _cache_key(self, key: str) -> str:
        return self._keys.cache(key)

    async def get(self, key: str) -> str | None:
        return await self._repository.get(self._cache_key(key))

    async def get_json(self, key: str) -> Any | None:
        return await self._repository.get_json(self._cache_key(key))

    async def set(
        self,
        key: str,
        value: str,
        *,
        ttl: int | None = None,
    ) -> bool:
        return await self._repository.set(
            self._cache_key(key),
            value,
            ex=ttl if ttl is not None else self._default_ttl,
        )

    async def set_json(
        self,
        key: str,
        value: Any,
        *,
        ttl: int | None = None,
    ) -> bool:
        return await self._repository.set_json(
            self._cache_key(key),
            value,
            ex=ttl if ttl is not None else self._default_ttl,
        )

    async def delete(self, key: str) -> int:
        return await self._repository.delete(self._cache_key(key))

    async def exists(self, key: str) -> bool:
        return (await self._repository.exists(self._cache_key(key))) > 0
