"""Smoke: monitoring cron + worker start/stop with MONITORING_ENABLED=true."""

from __future__ import annotations

import asyncio
import os

os.environ.setdefault("MONITORING_ENABLED", "true")
os.environ.setdefault("MONITORING_WORKER_ENABLED", "true")
os.environ.setdefault("REDIS_ENABLED", "false")

from app.core.config import get_settings
from app.infrastructure.redis.connection import RedisManager
from app.monitoring.monitoring_engine import MonitoringEngine
from app.repositories.redis_repository import RedisRepository


async def main() -> None:
    settings = get_settings()
    settings.MONITORING_ENABLED = True
    settings.MONITORING_WORKER_ENABLED = True
    manager = RedisManager(settings)
    repo = RedisRepository(manager)
    engine = MonitoringEngine(settings, repo)
    engine.start()
    status = await engine.status()
    assert status["enabled"] is True
    print("scheduler_running", status["scheduler_running"])
    print("worker_running", status["worker_running"])
    await engine.shutdown()
    print("smoke_ok")


if __name__ == "__main__":
    asyncio.run(main())
