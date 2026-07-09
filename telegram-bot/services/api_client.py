from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import httpx

logger = logging.getLogger(__name__)


class BackendError(Exception):
    """Base exception for backend integration failures."""


class BackendUnavailableError(BackendError):
    """Raised when backend cannot be reached after retries."""


class BackendRequestError(BackendError):
    """Raised for non-retriable backend request failures."""


class BackendResponseError(BackendError):
    """Raised when backend response payload is invalid."""


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int
    base_delay_seconds: float
    max_delay_seconds: float


def _is_transient_error(exc: Exception) -> bool:
    if isinstance(exc, (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        return status_code == 429 or 500 <= status_code < 600
    return False


@runtime_checkable
class ApiClient(Protocol):
    async def get_user_profile(self, telegram_id: int) -> dict[str, Any]: ...
    async def get_dashboard_stats(self, telegram_id: int) -> dict[str, Any]: ...
    async def get_watch_lists(self, telegram_id: int) -> dict[str, list[dict[str, Any]]]: ...
    async def get_follow_targets(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def get_following(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def get_mutual_followers(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def add_account(
        self, telegram_id: int, username: str, list_type: str = "follow_targets"
    ) -> dict[str, Any]: ...
    async def remove_account(
        self, telegram_id: int, username: str, list_type: str = "follow_targets"
    ) -> dict[str, Any]: ...
    async def get_notifications(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def get_target_achieved(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def get_settings(self, telegram_id: int) -> dict[str, Any]: ...
    async def update_settings(
        self, telegram_id: int, updates: dict[str, Any]
    ) -> dict[str, Any]: ...
    async def connect_x(self, telegram_id: int) -> dict[str, Any]: ...


class BackendHttpClient:
    def __init__(self, *, base_url: str, timeout_seconds: float, retry: RetryConfig) -> None:
        self._base_url = base_url.rstrip("/")
        self._retry = retry
        self._client = httpx.AsyncClient(timeout=timeout_seconds)

    async def request_json(
        self,
        method: str,
        path: str,
        *,
        telegram_id: int,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers = {"X-App-User-Id": str(telegram_id)}

        for attempt in range(1, self._retry.max_attempts + 1):
            try:
                response = await self._client.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    headers=headers,
                )
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise BackendResponseError("Backend payload must be a JSON object")
                return payload
            except Exception as exc:
                is_last = attempt >= self._retry.max_attempts
                if not _is_transient_error(exc) or is_last:
                    if isinstance(exc, httpx.HTTPStatusError):
                        raise BackendRequestError(
                            f"Backend request failed with status {exc.response.status_code}"
                        ) from exc
                    if isinstance(exc, BackendResponseError):
                        raise
                    raise BackendUnavailableError("Backend is unavailable") from exc

                delay = min(
                    self._retry.base_delay_seconds * (2 ** (attempt - 1)),
                    self._retry.max_delay_seconds,
                )
                logger.warning(
                    "backend_retry_scheduled",
                    extra={
                        "url": url,
                        "method": method,
                        "attempt": attempt,
                        "delay_seconds": delay,
                    },
                )
                await asyncio.sleep(delay)

        raise BackendUnavailableError("Backend is unavailable")


def create_api_client(*, settings: object | None = None) -> ApiClient:
    if settings is None:
        raise ValueError("settings are required")
    from services.http_backend import HttpApiClient

    return HttpApiClient(settings)
