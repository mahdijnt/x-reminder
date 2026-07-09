"""Async HTTP client for X API v2."""

from __future__ import annotations

import logging
import time
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any

import httpx

from app.core.config import Settings
from app.integrations.x import endpoints as ep
from app.integrations.x.exceptions import XAPIError, XNotFoundError, XRateLimitError
from app.integrations.x.models import (
    XOAuthTokenResponse,
    XTweetsListResponse,
    XUserResponse,
    XUsersListResponse,
)
from app.integrations.x.rate_limiter import log_rate_limit, parse_rate_limit_headers
from app.integrations.x.retry import with_retry

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from app.infrastructure.x.rate_limit_state import XRateLimitStateStore


class XAPIClient:
    """Low-level X API HTTP wrapper."""

    def __init__(
        self,
        settings: Settings,
        *,
        access_token: str | None = None,
        rate_limit_store: XRateLimitStateStore | None = None,
    ) -> None:
        self._settings = settings
        self._access_token = access_token
        self._rate_limit_store = rate_limit_store
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "XAPIClient":
        self._client = httpx.AsyncClient(timeout=self._settings.X_HTTP_TIMEOUT)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _headers(self, *, bearer: str | None = None) -> dict[str, str]:
        token = bearer or self._access_token or self._settings.X_BEARER_TOKEN
        if not token:
            raise XAPIError("No X access token configured", code="x_missing_token", status_code=401)
        return {"Authorization": f"Bearer {token}"}

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        endpoint_key: str = "unknown",
    ) -> dict[str, Any]:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._settings.X_HTTP_TIMEOUT)

        async def _do() -> dict[str, Any]:
            response = await self._client.request(method, url, params=params, data=data, headers=headers)
            rate_info = parse_rate_limit_headers(dict(response.headers))
            log_rate_limit(endpoint_key, rate_info)
            if self._rate_limit_store is not None:
                await self._rate_limit_store.save(endpoint_key, rate_info)

            if response.status_code == 429:
                retry_after = None
                if rate_info.reset is not None:
                    retry_after = max(0, int(rate_info.reset - time.time()))
                raise XRateLimitError(reset_at=rate_info.reset, retry_after=retry_after)
            if response.status_code == 404:
                raise XNotFoundError(response.text or "Not found")
            if response.status_code >= 400:
                raise XAPIError(
                    response.text or "X API request failed",
                    status_code=response.status_code,
                    details={"endpoint": endpoint_key},
                )

            try:
                return response.json()
            except JSONDecodeError as exc:
                raise XAPIError(
                    "Invalid JSON payload received from X API",
                    code="x_invalid_payload",
                    status_code=502,
                    details={"endpoint": endpoint_key},
                ) from exc

        logger.info("x_api_call", extra={"method": method, "endpoint": endpoint_key})
        return await with_retry(_do, settings=self._settings, operation_name=endpoint_key)

    async def get_me(self, *, user_fields: str | None = None) -> XUserResponse:
        params: dict[str, Any] = {}
        if user_fields:
            params["user.fields"] = user_fields
        payload = await self._request(
            "GET",
            ep.url(ep.USERS_ME),
            params=params,
            headers=self._headers(),
            endpoint_key="users/me",
        )
        return XUserResponse.model_validate(payload)

    async def get_user_by_username(self, username: str, *, user_fields: str | None = None) -> XUserResponse:
        params: dict[str, Any] = {}
        if user_fields:
            params["user.fields"] = user_fields
        payload = await self._request(
            "GET",
            ep.url(ep.USER_BY_USERNAME, username=username),
            params=params,
            headers=self._headers(),
            endpoint_key="users/by/username",
        )
        return XUserResponse.model_validate(payload)

    async def get_followers(
        self,
        user_id: str,
        *,
        pagination_token: str | None = None,
        max_results: int = 100,
    ) -> XUsersListResponse:
        params: dict[str, Any] = {"max_results": max_results, "user.fields": "id,name,username"}
        if pagination_token:
            params["pagination_token"] = pagination_token
        payload = await self._request(
            "GET",
            ep.url(ep.USER_FOLLOWERS, user_id=user_id),
            params=params,
            headers=self._headers(),
            endpoint_key="users/followers",
        )
        return XUsersListResponse.model_validate(payload)

    async def get_following(
        self,
        user_id: str,
        *,
        pagination_token: str | None = None,
        max_results: int = 100,
    ) -> XUsersListResponse:
        params: dict[str, Any] = {"max_results": max_results, "user.fields": "id,name,username"}
        if pagination_token:
            params["pagination_token"] = pagination_token
        payload = await self._request(
            "GET",
            ep.url(ep.USER_FOLLOWING, user_id=user_id),
            params=params,
            headers=self._headers(),
            endpoint_key="users/following",
        )
        return XUsersListResponse.model_validate(payload)

    async def get_user_tweets(
        self,
        user_id: str,
        *,
        since_id: str | None = None,
        pagination_token: str | None = None,
        max_results: int = 100,
    ) -> XTweetsListResponse:
        params: dict[str, Any] = {
            "max_results": max_results,
            "tweet.fields": "author_id,created_at,conversation_id,in_reply_to_user_id,referenced_tweets",
            "expansions": "author_id",
            "user.fields": "username",
        }
        if since_id:
            params["since_id"] = since_id
        if pagination_token:
            params["pagination_token"] = pagination_token
        payload = await self._request(
            "GET",
            ep.url(ep.USER_TWEETS, user_id=user_id),
            params=params,
            headers=self._headers(),
            endpoint_key="users/tweets",
        )
        return XTweetsListResponse.model_validate(payload)

    async def exchange_code_for_token(self, code: str, code_verifier: str) -> XOAuthTokenResponse:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._settings.X_CALLBACK_URL,
            "code_verifier": code_verifier,
            "client_id": self._settings.X_CLIENT_ID,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        auth = (self._settings.X_CLIENT_ID, self._settings.X_CLIENT_SECRET)
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._settings.X_HTTP_TIMEOUT)
        response = await self._client.post(ep.oauth_token_url(), data=data, headers=headers, auth=auth)
        if response.status_code >= 400:
            raise XAPIError(response.text, status_code=response.status_code, code="x_token_exchange_failed")
        return XOAuthTokenResponse.model_validate(response.json())

    async def refresh_access_token(self, refresh_token: str) -> XOAuthTokenResponse:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self._settings.X_CLIENT_ID,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        auth = (self._settings.X_CLIENT_ID, self._settings.X_CLIENT_SECRET)
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._settings.X_HTTP_TIMEOUT)
        response = await self._client.post(ep.oauth_token_url(), data=data, headers=headers, auth=auth)
        if response.status_code >= 400:
            raise XAPIError(response.text, status_code=response.status_code, code="x_token_refresh_failed")
        return XOAuthTokenResponse.model_validate(response.json())

    async def revoke_token(self, token: str) -> None:
        data = {"token": token, "token_type_hint": "refresh_token"}
        auth = (self._settings.X_CLIENT_ID, self._settings.X_CLIENT_SECRET)
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._settings.X_HTTP_TIMEOUT)
        response = await self._client.post(ep.oauth_revoke_url(), data=data, auth=auth)
        if response.status_code >= 400:
            raise XAPIError(response.text, status_code=response.status_code, code="x_token_revoke_failed")
