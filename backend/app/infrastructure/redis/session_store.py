"""Redis-backed session storage."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.infrastructure.redis.keys import RedisKeys, RedisTTL, get_redis_keys
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class SessionStore:
    """Store and retrieve session payloads by session_id."""

    def __init__(
        self,
        repository: RedisRepository,
        keys: RedisKeys | None = None,
        default_ttl: int = RedisTTL.SESSION,
    ) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()
        self._default_ttl = default_ttl

    async def save(
        self,
        session_id: str,
        data: dict[str, Any],
        *,
        ttl: int | None = None,
    ) -> bool:
        key = self._keys.session(session_id)
        return await self._repository.set_json(
            key,
            data,
            ex=ttl if ttl is not None else self._default_ttl,
        )

    async def get(self, session_id: str) -> dict[str, Any] | None:
        key = self._keys.session(session_id)
        payload = await self._repository.get_json(key)
        if isinstance(payload, dict):
            return payload
        return None

    async def delete(self, session_id: str) -> int:
        return await self._repository.delete(self._keys.session(session_id))

    async def refresh_ttl(self, session_id: str, ttl: int | None = None) -> bool:
        return await self._repository.expire(
            self._keys.session(session_id),
            ttl if ttl is not None else self._default_ttl,
        )

    async def exists(self, session_id: str) -> bool:
        return (await self._repository.exists(self._keys.session(session_id))) > 0
