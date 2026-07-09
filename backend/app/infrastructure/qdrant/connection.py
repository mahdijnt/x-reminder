"""Async Qdrant client manager with reconnection."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import Settings, get_settings
from app.infrastructure.qdrant.exceptions import QdrantConnectionError, QdrantUnavailableError

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

T = TypeVar("T")

_manager: "QdrantManager | None" = None


class QdrantManager:
    """Singleton async Qdrant manager."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncQdrantClient | None = None
        self._lock = asyncio.Lock()
        self._collection_count: int | None = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    @property
    def collection_count(self) -> int | None:
        return self._collection_count

    async def connect(self) -> None:
        if not self._settings.QDRANT_ENABLED:
            logger.info("qdrant_disabled", extra={"event": "qdrant_connect_skipped"})
            return

        async with self._lock:
            if self.is_connected:
                return
            self._client = AsyncQdrantClient(
                url=self._settings.QDRANT_URL,
                api_key=self._settings.QDRANT_API_KEY or None,
                timeout=self._settings.QDRANT_TIMEOUT_SECONDS,
            )

        try:
            await self._ping_with_retry()
            logger.info(
                "qdrant_connected",
                extra={"event": "qdrant_connect", "url": _sanitize_url(self._settings.QDRANT_URL)},
            )
        except Exception as exc:
            logger.warning(
                "qdrant_connect_failed",
                extra={"event": "qdrant_connect_failed", "error": str(exc)},
            )
            await self._teardown()

    async def disconnect(self) -> None:
        async with self._lock:
            await self._teardown_unlocked()
        logger.info("qdrant_disconnected", extra={"event": "qdrant_disconnect"})

    async def ping(self) -> bool:
        if not self._settings.QDRANT_ENABLED:
            return False
        if not self.is_connected:
            return False
        try:
            assert self._client is not None
            collections = await self._client.get_collections()
            self._collection_count = len(collections.collections)
            return True
        except Exception as exc:
            logger.warning(
                "qdrant_ping_failed",
                extra={"event": "qdrant_ping_failed", "error": str(exc)},
            )
            return False

    def get_client(self) -> AsyncQdrantClient:
        if not self.is_connected or self._client is None:
            raise QdrantUnavailableError("Qdrant client is not connected")
        return self._client

    async def ensure_client(self) -> AsyncQdrantClient | None:
        if not self._settings.QDRANT_ENABLED:
            return None
        if self.is_connected and await self.ping():
            return self._client
        await self.connect()
        if self.is_connected and await self.ping():
            return self._client
        return None

    async def execute(
        self,
        operation: Callable[[AsyncQdrantClient], Awaitable[T]],
        *,
        retry: bool = True,
    ) -> T:
        if not self._settings.QDRANT_ENABLED:
            raise QdrantUnavailableError("Qdrant is disabled")

        last_error: Exception | None = None
        attempts = self._settings.QDRANT_RETRY_MAX_ATTEMPTS if retry else 1

        for attempt in range(1, attempts + 1):
            client = await self.ensure_client()
            if client is None:
                raise QdrantUnavailableError("Qdrant is unavailable")

            try:
                return await operation(client)
            except (UnexpectedResponse, OSError, TimeoutError) as exc:
                last_error = exc
                logger.warning(
                    "qdrant_operation_failed",
                    extra={
                        "event": "qdrant_operation_failed",
                        "attempt": attempt,
                        "error": str(exc),
                    },
                )
                async with self._lock:
                    await self._teardown_unlocked()
                if attempt < attempts:
                    await asyncio.sleep(_backoff_delay(self._settings, attempt))

        raise QdrantConnectionError(
            "Qdrant operation failed after retries",
            details={"error": str(last_error) if last_error else "unknown"},
        )

    async def _ping_with_retry(self) -> None:
        assert self._client is not None
        for attempt in range(1, self._settings.QDRANT_RETRY_MAX_ATTEMPTS + 1):
            try:
                collections = await self._client.get_collections()
                self._collection_count = len(collections.collections)
                return
            except Exception as exc:
                logger.warning(
                    "qdrant_connect_retry",
                    extra={"attempt": attempt, "error": str(exc)},
                )
                if attempt >= self._settings.QDRANT_RETRY_MAX_ATTEMPTS:
                    raise
                await asyncio.sleep(_backoff_delay(self._settings, attempt))

    async def _teardown(self) -> None:
        async with self._lock:
            await self._teardown_unlocked()

    async def _teardown_unlocked(self) -> None:
        if self._client is not None:
            try:
                await self._client.close()
            except Exception as exc:
                logger.debug("qdrant_client_close_error", extra={"error": str(exc)})
            self._client = None
        self._collection_count = None

    async def __aenter__(self) -> "QdrantManager":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.disconnect()


def get_qdrant_manager(settings: Settings | None = None) -> QdrantManager:
    global _manager
    if _manager is None:
        _manager = QdrantManager(settings or get_settings())
    return _manager


def reset_qdrant_manager() -> None:
    global _manager
    _manager = None


def _backoff_delay(settings: Settings, attempt: int) -> float:
    delay = settings.QDRANT_RETRY_BASE_DELAY * (2 ** (attempt - 1))
    return min(delay, settings.QDRANT_RETRY_MAX_DELAY)


def _sanitize_url(url: str) -> str:
    if "@" in url:
        scheme, rest = url.split("://", 1)
        if "@" in rest:
            _creds, host = rest.rsplit("@", 1)
            return f"{scheme}://***@{host}"
    return url