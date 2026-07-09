"""Short-lived temporary key storage (OTP placeholders, temp tokens)."""

from __future__ import annotations

import logging
from typing import Any

from app.infrastructure.redis.keys import RedisKeys, get_redis_keys, get_redis_ttl
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class TempStore:
    """Store short-lived values scoped by purpose and token id."""

    def __init__(
        self,
        repository: RedisRepository,
        keys: RedisKeys | None = None,
        default_ttl: int | None = None,
    ) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()
        self._default_ttl = default_ttl if default_ttl is not None else get_redis_ttl().temp_token

    async def put(
        self,
        purpose: str,
        token_id: str,
        value: str,
        *,
        ttl: int | None = None,
    ) -> bool:
        return await self._repository.set(
            self._keys.temp(purpose, token_id),
            value,
            ex=ttl if ttl is not None else self._default_ttl,
        )

    async def put_json(
        self,
        purpose: str,
        token_id: str,
        value: dict[str, Any],
        *,
        ttl: int | None = None,
    ) -> bool:
        return await self._repository.set_json(
            self._keys.temp(purpose, token_id),
            value,
            ex=ttl if ttl is not None else self._default_ttl,
        )

    async def get(self, purpose: str, token_id: str) -> str | None:
        return await self._repository.get(self._keys.temp(purpose, token_id))

    async def get_json(self, purpose: str, token_id: str) -> dict[str, Any] | None:
        payload = await self._repository.get_json(self._keys.temp(purpose, token_id))
        if isinstance(payload, dict):
            return payload
        return None

    async def delete(self, purpose: str, token_id: str) -> int:
        return await self._repository.delete(self._keys.temp(purpose, token_id))
