"""Internal Redis utilities for development and diagnostics."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings
from app.infrastructure.redis.connection import RedisManager

logger = logging.getLogger(__name__)


async def ping_redis(manager: RedisManager) -> bool:
    return await manager.ping()


async def flush_redis_dev_only(settings: Settings, manager: RedisManager) -> bool:
    """Flush the current Redis DB; allowed only in development."""
    if not settings.is_development:
        logger.warning(
            "redis_flush_denied",
            extra={"event": "redis_flush_denied", "environment": settings.ENVIRONMENT.value},
        )
        return False
    if not settings.REDIS_ENABLED:
        return False

    async def _op(client):
        await client.flushdb()
        return True

    try:
        await manager.execute(_op)
        logger.info("redis_flush_dev", extra={"event": "redis_flush_dev"})
        return True
    except Exception as exc:
        logger.warning("redis_flush_failed", extra={"error": str(exc)})
        return False


def validate_redis_config(settings: Settings) -> dict[str, Any]:
    """Return validation metadata for Redis configuration."""
    issues: list[str] = []
    if settings.REDIS_ENABLED and not settings.REDIS_URL:
        issues.append("REDIS_ENABLED=true but no REDIS_URL could be resolved")
    if settings.REDIS_MAX_CONNECTIONS < 1:
        issues.append("REDIS_MAX_CONNECTIONS must be >= 1")
    if settings.REDIS_SOCKET_TIMEOUT <= 0:
        issues.append("REDIS_SOCKET_TIMEOUT must be > 0")
    return {
        "valid": not issues,
        "issues": issues,
        "url_configured": bool(settings.REDIS_URL),
        "ssl": settings.REDIS_SSL,
        "db": settings.REDIS_DB,
    }
