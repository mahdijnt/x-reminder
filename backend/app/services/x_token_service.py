"""Access token refresh helper."""

from __future__ import annotations

import logging
import time

from app.core.config import Settings
from app.integrations.x.client import XAPIClient
from app.integrations.x.exceptions import XTokenError
from app.integrations.x.models import StoredXTokens
from app.infrastructure.x.token_store import XTokenStore

logger = logging.getLogger(__name__)


class XTokenService:
    def __init__(self, settings: Settings, token_store: XTokenStore) -> None:
        self._settings = settings
        self._token_store = token_store

    async def get_stored_x_user_id(self, app_user_id: str) -> str | None:
        tokens = await self._token_store.get_tokens(app_user_id)
        return tokens.x_user_id if tokens else None

    async def get_access_token(self, app_user_id: str) -> str:
        token = await self._token_store.get_valid_access_token(app_user_id)
        if token:
            return token
        tokens = await self._token_store.get_tokens(app_user_id)
        if tokens is None or not tokens.refresh_token:
            raise XTokenError("X account not connected")
        async with XAPIClient(self._settings) as client:
            refreshed = await client.refresh_access_token(tokens.refresh_token)
        expires_at = int(time.time()) + int(refreshed.expires_in)
        updated = StoredXTokens(
            access_token=refreshed.access_token,
            refresh_token=refreshed.refresh_token or tokens.refresh_token,
            expires_at=expires_at,
            scope=refreshed.scope or tokens.scope,
            x_user_id=tokens.x_user_id,
            token_type=refreshed.token_type,
        )
        await self._token_store.update_after_refresh(app_user_id, updated)
        logger.info("x_token_refreshed", extra={"app_user_id": app_user_id})
        return updated.access_token
