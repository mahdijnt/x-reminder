"""Async Redis connection manager with pooling and reconnection."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import AuthenticationError, RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.core.config import Settings, get_settings
from app.core.exceptions import RedisConnectionError, RedisUnavailableError

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

T = TypeVar("T")

_manager: "RedisManager | None" = None


class RedisManager:
    """Singleton async Redis manager backed by a shared connection pool."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None
        self._lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._pool is not None

    async def connect(self) -> None:
        """Create the connection pool and verify connectivity."""
        if not self._settings.REDIS_ENABLED:
            logger.info("redis_disabled", extra={"event": "redis_connect_skipped"})
            return

        async with self._lock:
            if self.is_connected:
                return
            await self._create_pool()

        try:
            await self._ping_with_retry()
            logger.info(
                "redis_connected",
                extra={
                    "event": "redis_connect",
                    "url": _sanitize_url(self._settings.REDIS_URL),
                },
            )
        except RedisError as exc:
            logger.warning(
                "redis_connect_failed",
                extra={"event": "redis_connect_failed", "error": str(exc)},
            )
            await self._teardown()

    async def disconnect(self) -> None:
        """Close the Redis client and connection pool."""
        async with self._lock:
            await self._teardown()
        logger.info("redis_disconnected", extra={"event": "redis_disconnect"})

    async def ping(self) -> bool:
        """Return True if Redis responds to PING."""
        if not self._settings.REDIS_ENABLED:
            return False
        if not self.is_connected:
            return False
        try:
            assert self._client is not None
            result = await self._client.ping()
            return bool(result)
        except RedisError as exc:
            logger.warning(
                "redis_ping_failed",
                extra={"event": "redis_ping_failed", "error": str(exc)},
            )
            return False

    def get_client(self) -> Redis:
        """Return the shared Redis client (raises if not connected)."""
        if not self.is_connected or self._client is None:
            raise RedisUnavailableError("Redis client is not connected")
        return self._client

    async def ensure_client(self) -> Redis | None:
        """Ensure a working client, attempting reconnect on failure."""
        if not self._settings.REDIS_ENABLED:
            return None
        if self.is_connected:
            if await self.ping():
                return self._client
        await self.connect()
        if self.is_connected:
            return self._client
        return None


    def pool_status(self) -> dict[str, Any]:
        """Return best-effort connection pool metrics."""
        if self._pool is None:
            return {
                "status": "disconnected",
                "max_connections": self._settings.REDIS_MAX_CONNECTIONS,
                "in_use": 0,
                "available": 0,
                "exhausted": False,
            }
        in_use = len(getattr(self._pool, "_in_use_connections", set()) or [])
        available = len(getattr(self._pool, "_available_connections", []) or [])
        max_conn = self._settings.REDIS_MAX_CONNECTIONS
        return {
            "status": "connected" if self.is_connected else "disconnected",
            "max_connections": max_conn,
            "in_use": in_use,
            "available": available,
            "exhausted": self.is_connected and in_use >= max_conn and available == 0,
        }

    async def health_snapshot(self) -> dict[str, Any]:
        """Collect connectivity, latency, pool, and server version for health checks."""
        pool = self.pool_status()
        if not self._settings.REDIS_ENABLED:
            return {
                "connected": False,
                "latency_ms": None,
                "pool": pool,
                "server_version": None,
                "detail": "REDIS_ENABLED=false",
            }
        client = await self.ensure_client()
        if client is None:
            return {
                "connected": False,
                "latency_ms": None,
                "pool": pool,
                "server_version": None,
                "detail": "Redis client unavailable",
            }
        started = time.perf_counter()
        try:
            await client.ping()
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            info = await client.info(section="server")
            version = info.get("redis_version") if isinstance(info, dict) else None
            return {
                "connected": True,
                "latency_ms": latency_ms,
                "pool": pool,
                "server_version": version,
                "detail": None,
            }
        except RedisError as exc:
            _log_redis_error("redis_health_failed", exc)
            return {
                "connected": False,
                "latency_ms": None,
                "pool": self.pool_status(),
                "server_version": None,
                "detail": str(exc),
            }

    async def execute(
        self,
        operation: Callable[[Redis], Awaitable[T]],
        *,
        retry: bool = True,
    ) -> T:
        """Run an operation with optional retry and reconnection."""
        if not self._settings.REDIS_ENABLED:
            raise RedisUnavailableError("Redis is disabled")

        last_error: Exception | None = None
        attempts = self._settings.REDIS_RETRY_MAX_ATTEMPTS if retry else 1

        for attempt in range(1, attempts + 1):
            client = await self.ensure_client()
            if client is None:
                raise RedisUnavailableError("Redis is unavailable")

            try:
                return await operation(client)
            except RedisError as exc:
                last_error = exc
                _log_redis_error("redis_operation_failed", exc, attempt=attempt)
                await self._teardown_unlocked()
                if attempt < attempts:
                    await asyncio.sleep(_backoff_delay(self._settings, attempt))

        raise RedisConnectionError(
            "Redis operation failed after retries",
            details={"error": str(last_error) if last_error else "unknown"},
        )

    async def _create_pool(self) -> None:
        self._pool = ConnectionPool.from_url(
            self._settings.REDIS_URL,
            max_connections=self._settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=self._settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=self._settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            health_check_interval=self._settings.REDIS_HEALTH_CHECK_INTERVAL,
            decode_responses=True,
            retry_on_timeout=True,
        )
        self._client = Redis(connection_pool=self._pool)

    async def _ping_with_retry(self) -> None:
        assert self._client is not None
        for attempt in range(1, self._settings.REDIS_RETRY_MAX_ATTEMPTS + 1):
            try:
                await self._client.ping()
                return
            except RedisError as exc:
                logger.warning(
                    "redis_connect_retry",
                    extra={"attempt": attempt, "error": str(exc)},
                )
                if attempt >= self._settings.REDIS_RETRY_MAX_ATTEMPTS:
                    raise
                await asyncio.sleep(_backoff_delay(self._settings, attempt))

    async def _teardown(self) -> None:
        await self._teardown_unlocked()

    async def _teardown_unlocked(self) -> None:
        if self._client is not None:
            try:
                await self._client.aclose()
            except RedisError as exc:
                logger.debug("redis_client_close_error", extra={"error": str(exc)})
            self._client = None
        if self._pool is not None:
            try:
                await self._pool.aclose()
            except RedisError as exc:
                logger.debug("redis_pool_close_error", extra={"error": str(exc)})
            self._pool = None

    async def __aenter__(self) -> RedisManager:
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.disconnect()


def get_redis_manager(settings: Settings | None = None) -> RedisManager:
    """Return the process-wide Redis manager singleton."""
    global _manager
    if _manager is None:
        _manager = RedisManager(settings or get_settings())
    return _manager


def reset_redis_manager() -> None:
    """Reset singleton (tests)."""
    global _manager
    _manager = None


def _backoff_delay(settings: Settings, attempt: int) -> float:
    delay = settings.REDIS_RETRY_BASE_DELAY * (2 ** (attempt - 1))
    return min(delay, settings.REDIS_RETRY_MAX_DELAY)


def _sanitize_url(url: str) -> str:
    if "@" in url:
        scheme, rest = url.split("://", 1)
        if "@" in rest:
            creds, host = rest.rsplit("@", 1)
            return f"{scheme}://***@{host}"
    return url


def _log_redis_error(event: str, exc: Exception, **extra: Any) -> None:
    payload: dict[str, Any] = {"event": event, "error": str(exc), **extra}
    if isinstance(exc, AuthenticationError):
        payload["reason"] = "auth_failure"
        logger.error(event, extra=payload)
    elif isinstance(exc, RedisTimeoutError):
        payload["reason"] = "timeout"
        logger.warning(event, extra=payload)
    else:
        payload["reason"] = "connection_or_command"
        logger.warning(event, extra=payload)
