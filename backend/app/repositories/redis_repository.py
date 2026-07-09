"""Generic Redis key-value repository."""

from __future__ import annotations

import logging
from typing import Any

from redis.asyncio import Redis

from app.infrastructure.redis.connection import RedisManager
from app.core.exceptions import RedisConnectionError, RedisUnavailableError
from app.infrastructure.redis.serialization import (
    RedisSerializationError,
    serialize_json,
    try_deserialize_json,
)

logger = logging.getLogger(__name__)


class RedisRepository:
    """Low-level Redis operations with graceful error handling."""

    def __init__(self, manager: RedisManager) -> None:
        self._manager = manager

    async def get(self, key: str) -> str | None:
        async def _op(client: Redis) -> str | None:
            return await client.get(key)

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            logger.debug("redis_get_skipped", extra={"key": key})
            return None

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
        px: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        async def _op(client: Redis) -> bool:
            result = await client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            return bool(result)

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return False

    async def delete(self, *keys: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.delete(*keys))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def exists(self, *keys: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.exists(*keys))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def expire(self, key: str, seconds: int) -> bool:
        async def _op(client: Redis) -> bool:
            return bool(await client.expire(key, seconds))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return False

    async def ttl(self, key: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.ttl(key))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return -2

    async def mget(self, keys: list[str]) -> list[str | None]:
        if not keys:
            return []

        async def _op(client: Redis) -> list[str | None]:
            return list(await client.mget(keys))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return [None for _ in keys]

    async def mset(self, mapping: dict[str, str]) -> bool:
        if not mapping:
            return True

        async def _op(client: Redis) -> bool:
            await client.mset(mapping)
            return True

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return False

    async def hget(self, name: str, key: str) -> str | None:
        async def _op(client: Redis) -> str | None:
            return await client.hget(name, key)

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return None

    async def hset(self, name: str, key: str, value: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.hset(name, key, value))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def hgetall(self, name: str) -> dict[str, str]:
        async def _op(client: Redis) -> dict[str, str]:
            data = await client.hgetall(name)
            return dict(data)

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return {}

    async def hdel(self, name: str, *keys: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.hdel(name, *keys))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def get_json(self, key: str) -> Any | None:
        raw = await self.get(key)
        if raw is None:
            return None
        parsed = try_deserialize_json(raw)
        if parsed is None and raw:
            logger.warning("redis_json_decode_failed", extra={"key": key})
        return parsed

    async def set_json(self, key: str, value: Any, *, ex: int | None = None) -> bool:
        try:
            payload = serialize_json(value)
        except RedisSerializationError:
            return False
        return await self.set(key, payload, ex=ex)

    async def rpush(self, key: str, value: str) -> bool:
        async def _op(client: Redis) -> bool:
            await client.rpush(key, value)
            return True

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return False

    async def lpop(self, key: str) -> str | None:
        async def _op(client: Redis) -> str | None:
            return await client.lpop(key)

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return None

    async def llen(self, key: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.llen(key))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def zadd(self, key: str, mapping: dict[str, float]) -> bool:
        async def _op(client: Redis) -> bool:
            await client.zadd(key, mapping)
            return True

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return False

    async def zrem(self, key: str, member: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.zrem(key, member))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def zrangebyscore(
        self,
        key: str,
        min_score: float,
        max_score: float,
        *,
        start: int = 0,
        num: int = -1,
    ) -> list[str]:
        async def _op(client: Redis) -> list[str]:
            return list(await client.zrangebyscore(key, min_score, max_score, start=start, num=num))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return []

    async def zcard(self, key: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.zcard(key))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def zrevrange(self, key: str, start: int, end: int) -> list[str]:
        async def _op(client: Redis) -> list[str]:
            return list(await client.zrevrange(key, start, end))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return []

    async def hincrby(self, name: str, key: str, amount: int = 1) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.hincrby(name, key, amount))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0



    async def incr(self, key: str, amount: int = 1) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.incrby(key, amount))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def delete_by_pattern(self, pattern: str, *, count: int = 100) -> int:
        async def _op(client: Redis) -> int:
            deleted = 0
            async for key in client.scan_iter(match=pattern, count=count):
                deleted += int(await client.delete(key))
            return deleted

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0
