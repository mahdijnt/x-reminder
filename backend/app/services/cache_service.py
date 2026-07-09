"""Application-level cache with TTL and namespacing."""

from __future__ import annotations

import logging
from typing import Any

from app.infrastructure.redis.keys import RedisKeys, get_redis_keys, get_redis_ttl
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class CacheService:
    """High-level cache for arbitrary application data."""

    def __init__(
        self,
        repository: RedisRepository,
        keys: RedisKeys | None = None,
        default_ttl: int | None = None,
    ) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()
        self._default_ttl = default_ttl if default_ttl is not None else get_redis_ttl().cache_default

    def _cache_key(self, key: str) -> str:
        return self._keys.cache(key)

    async def get(self, key: str) -> str | None:
        value = await self._repository.get(self._cache_key(key))
        if value is None:
            logger.debug("cache_miss", extra={"event": "cache_miss", "key": key})
        else:
            logger.debug("cache_hit", extra={"event": "cache_hit", "key": key})
        return value

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


    async def increment(self, key: str, amount: int = 1) -> int:
        return await self._repository.incr(self._cache_key(key), amount)

    async def expire(self, key: str, ttl: int) -> bool:
        return await self._repository.expire(self._cache_key(key), ttl)

    async def delete_by_pattern(self, pattern: str) -> int:
        return await self._repository.delete_by_pattern(self._cache_key(pattern))
