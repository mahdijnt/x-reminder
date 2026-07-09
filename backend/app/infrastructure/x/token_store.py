"""Encrypted OAuth token storage in Redis."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, RedisTTL, get_redis_keys
from app.infrastructure.x.encryption import decrypt_value, encrypt_value
from app.integrations.x.exceptions import XTokenError
from app.integrations.x.models import StoredXTokens
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class XTokenStore:
    def __init__(
        self,
        repository: RedisRepository,
        settings: Settings,
        keys: RedisKeys | None = None,
    ) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()

    def _key(self, app_user_id: str) -> str:
        return self._keys.x_oauth_tokens(app_user_id)

    async def save_tokens(self, app_user_id: str, tokens: StoredXTokens) -> bool:
        payload = tokens.model_dump()
        encrypted = encrypt_value(self._settings, json.dumps(payload))
        return await self._repository.set(self._key(app_user_id), encrypted, ex=RedisTTL.CACHE_LONG * 24)

    async def get_tokens(self, app_user_id: str) -> StoredXTokens | None:
        raw = await self._repository.get(self._key(app_user_id))
        if not raw:
            return None
        try:
            decrypted = decrypt_value(self._settings, raw)
            data = json.loads(decrypted)
            return StoredXTokens.model_validate(data)
        except (ValueError, json.JSONDecodeError) as exc:
            logger.warning("x_token_decrypt_failed", extra={"app_user_id": app_user_id, "error": str(exc)})
            return None

    async def delete_tokens(self, app_user_id: str) -> int:
        return await self._repository.delete(self._key(app_user_id))

    async def get_valid_access_token(self, app_user_id: str) -> str | None:
        tokens = await self.get_tokens(app_user_id)
        if tokens is None:
            return None
        now = int(time.time())
        if tokens.expires_at and tokens.expires_at <= now + 30:
            return None
        return tokens.access_token

    async def update_after_refresh(self, app_user_id: str, tokens: StoredXTokens) -> bool:
        return await self.save_tokens(app_user_id, tokens)
