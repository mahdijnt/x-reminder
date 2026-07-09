"""X OAuth 2.0 PKCE service."""

from __future__ import annotations

import logging
import time

from app.core.config import Settings
from app.integrations.x.auth import build_authorization_url, generate_pkce_pair, generate_state
from app.integrations.x.client import XAPIClient
from app.integrations.x.exceptions import XAPIError, XAuthError
from app.integrations.x.models import StoredXTokens
from app.infrastructure.redis.temp_store import TempStore
from app.infrastructure.x.token_store import XTokenStore

logger = logging.getLogger(__name__)

PKCE_PURPOSE = "x_oauth_pkce"


class XOAuthService:
    def __init__(
        self,
        settings: Settings,
        temp_store: TempStore,
        token_store: XTokenStore,
    ) -> None:
        self._settings = settings
        self._temp_store = temp_store
        self._token_store = token_store

    async def create_authorization(self, app_user_id: str) -> tuple[str, str]:
        state = generate_state()
        verifier, challenge = generate_pkce_pair()
        await self._temp_store.put_json(
            PKCE_PURPOSE,
            state,
            {"code_verifier": verifier, "app_user_id": app_user_id},
        )
        url = build_authorization_url(self._settings, state=state, code_challenge=challenge)
        return url, state

    async def handle_callback(self, code: str, state: str) -> tuple[str, StoredXTokens, str | None]:
        session = await self._temp_store.get_json(PKCE_PURPOSE, state)
        if not session:
            raise XAPIError("Invalid or expired OAuth state", code="x_oauth_state_invalid", status_code=400)
        app_user_id = str(session["app_user_id"])
        verifier = str(session["code_verifier"])
        async with XAPIClient(self._settings) as client:
            token_response = await client.exchange_code_for_token(code, verifier)
        async with XAPIClient(self._settings, access_token=token_response.access_token) as authed:
            me = await authed.get_me(user_fields="id,username")
        if me.data is None:
            raise XAuthError("X OAuth completed but profile data is missing", code="x_oauth_profile_missing", status_code=502)
        expires_at = int(time.time()) + int(token_response.expires_in)
        stored = StoredXTokens(
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            expires_at=expires_at,
            scope=token_response.scope,
            x_user_id=me.data.id,
            token_type=token_response.token_type,
        )
        await self._token_store.save_tokens(app_user_id, stored)
        await self._temp_store.delete(PKCE_PURPOSE, state)
        username = me.data.username
        logger.info("x_oauth_connected", extra={"app_user_id": app_user_id, "x_user_id": stored.x_user_id})
        return app_user_id, stored, username

    async def disconnect(self, app_user_id: str) -> bool:
        tokens = await self._token_store.get_tokens(app_user_id)
        if tokens and tokens.refresh_token:
            try:
                async with XAPIClient(self._settings) as client:
                    await client.revoke_token(tokens.refresh_token)
            except XAPIError:
                logger.warning("x_oauth_revoke_failed", extra={"app_user_id": app_user_id})
        deleted = await self._token_store.delete_tokens(app_user_id)
        return deleted > 0
