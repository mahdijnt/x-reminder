"""Rate limiting with optional Redis-backed sliding window."""

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from time import monotonic

from fastapi import Request

from app.core.config import Settings
from app.infrastructure.redis.connection import RedisManager
from app.infrastructure.redis.rate_limit_store import RedisRateLimitStore

logger = logging.getLogger(__name__)


@dataclass
class RateLimitState:
    """In-memory sliding window counters per client key."""

    windows: dict[str, deque[float]] = field(default_factory=lambda: defaultdict(deque))


class RateLimiter:
    """Rate limiter using Redis when available, otherwise in-memory fallback."""

    def __init__(
        self,
        settings: Settings,
        redis_manager: RedisManager | None = None,
    ) -> None:
        self._settings = settings
        self._state = RateLimitState()
        self._redis_store: RedisRateLimitStore | None = None
        if redis_manager is not None and settings.REDIS_ENABLED:
            self._redis_store = RedisRateLimitStore(redis_manager)

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def is_allowed(self, request: Request) -> bool:
        if not self._settings.RATE_LIMIT_ENABLED:
            return True

        key = self._client_key(request)
        if self._redis_store is not None:
            return await self._redis_store.is_allowed(
                key,
                limit=self._settings.RATE_LIMIT_REQUESTS,
                window_seconds=self._settings.RATE_LIMIT_WINDOW_SECONDS,
            )
        return self._is_allowed_memory(key)

    def is_allowed_sync(self, request: Request) -> bool:
        """Synchronous check for middleware that cannot await (memory only)."""
        if not self._settings.RATE_LIMIT_ENABLED:
            return True
        if self._redis_store is not None:
            logger.debug("ratelimit_use_async_is_allowed_for_redis")
        return self._is_allowed_memory(self._client_key(request))

    def _is_allowed_memory(self, key: str) -> bool:
        now = monotonic()
        window = self._settings.RATE_LIMIT_WINDOW_SECONDS
        limit = self._settings.RATE_LIMIT_REQUESTS
        bucket = self._state.windows[key]

        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= limit:
            return False

        bucket.append(now)
        return True


def get_rate_limiter(settings: Settings, redis_manager: RedisManager | None = None) -> RateLimiter:
    return RateLimiter(settings, redis_manager=redis_manager)
