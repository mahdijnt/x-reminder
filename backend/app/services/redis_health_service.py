"""Dedicated Redis health diagnostics."""

from __future__ import annotations

from app.core.config import Settings
from app.infrastructure.redis.connection import RedisManager
from app.schemas.health import RedisHealthData


class RedisHealthService:
    def __init__(self, settings: Settings, redis_manager: RedisManager) -> None:
        self._settings = settings
        self._redis_manager = redis_manager

    async def get_health(self) -> RedisHealthData:
        if not self._settings.REDIS_ENABLED:
            return RedisHealthData(
                connected=False,
                latency_ms=None,
                pool={"status": "disabled"},
                server_version=None,
                detail="REDIS_ENABLED=false",
            )
        payload = await self._redis_manager.health_snapshot()
        return RedisHealthData(**payload)
