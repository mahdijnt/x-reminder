"""Persist X API rate limit headers in Redis."""

from __future__ import annotations

from app.infrastructure.redis.keys import RedisKeys, RedisTTL, get_redis_keys
from app.integrations.x.models import XRateLimitInfo
from app.repositories.redis_repository import RedisRepository


class XRateLimitStateStore:
    def __init__(self, repository: RedisRepository, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()

    async def save(self, endpoint: str, info: XRateLimitInfo) -> bool:
        return await self._repository.set_json(
            self._keys.x_rate_limit(endpoint),
            info.model_dump(),
            ex=RedisTTL.CACHE_DEFAULT,
        )

    async def get(self, endpoint: str) -> XRateLimitInfo | None:
        payload = await self._repository.get_json(self._keys.x_rate_limit(endpoint))
        if not payload:
            return None
        return XRateLimitInfo.model_validate(payload)
