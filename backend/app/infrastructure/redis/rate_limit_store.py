"""Redis-backed rate limit storage (sliding window)."""

from __future__ import annotations

import logging
import time
import uuid

from redis.asyncio import Redis

from app.infrastructure.redis.connection import RedisManager
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.core.exceptions import RedisUnavailableError

logger = logging.getLogger(__name__)


class RedisRateLimitStore:
    """Sliding-window counter using a sorted set per client key."""

    def __init__(self, manager: RedisManager, keys: RedisKeys | None = None) -> None:
        self._manager = manager
        self._keys = keys or get_redis_keys()

    async def is_allowed(self, client_key: str, *, limit: int, window_seconds: int) -> bool:
        if limit <= 0:
            return True

        now = time.time()
        window_start = now - window_seconds
        member = f"{now}:{uuid.uuid4().hex}"
        redis_key = self._keys.ratelimit_sliding(client_key)

        async def _op(client: Redis) -> bool:
            pipe = client.pipeline(transaction=True)
            pipe.zremrangebyscore(redis_key, 0, window_start)
            pipe.zadd(redis_key, {member: now})
            pipe.zcard(redis_key)
            pipe.expire(redis_key, window_seconds + 1)
            results = await pipe.execute()
            count = int(results[2])
            if count > limit:
                await client.zrem(redis_key, member)
                return False
            return True

        try:
            return await self._manager.execute(_op)
        except RedisUnavailableError:
            logger.warning(
                "ratelimit_redis_unavailable",
                extra={"client_key": client_key},
            )
            return True
