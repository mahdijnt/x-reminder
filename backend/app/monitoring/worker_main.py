# Standalone monitoring worker entry point.

import asyncio
import logging

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.redis.connection import get_redis_manager
from app.monitoring.monitoring_engine import MonitoringEngine
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


async def _run() -> None:
    settings = get_settings()
    configure_logging(settings)
    manager = get_redis_manager(settings)
    await manager.connect()
    engine = MonitoringEngine(settings, RedisRepository(manager))
    engine.start()
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await engine.shutdown()
        await manager.disconnect()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
