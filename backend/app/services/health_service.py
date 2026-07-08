"""Health check business service."""

from datetime import datetime, timezone

from app.core.config import Settings
from app.infrastructure.redis.connection import RedisManager
from app.repositories.base import InMemoryRepository
from app.schemas.health import HealthCheckItem, HealthData


class HealthService:
    def __init__(
        self,
        settings: Settings,
        repository: InMemoryRepository,
        redis_manager: RedisManager | None = None,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._redis_manager = redis_manager

    async def get_health(self) -> HealthData:
        _ = await self._repository.list_all()

        checks: dict[str, HealthCheckItem] = {}
        overall = "ok"

        if self._settings.REDIS_ENABLED:
            if self._redis_manager is None:
                checks["redis"] = HealthCheckItem(
                    status="unavailable",
                    detail="Redis manager not initialized",
                )
                overall = "degraded"
            else:
                redis_ok = await self._redis_manager.ping()
                if redis_ok:
                    checks["redis"] = HealthCheckItem(status="ok")
                else:
                    checks["redis"] = HealthCheckItem(
                        status="unavailable",
                        detail="Redis ping failed or not connected",
                    )
                    overall = "degraded"
        else:
            checks["redis"] = HealthCheckItem(status="disabled", detail="REDIS_ENABLED=false")

        return HealthData(
            status=overall,
            version=self._settings.APP_VERSION,
            environment=self._settings.ENVIRONMENT.value,
            timestamp=datetime.now(timezone.utc),
            checks=checks,
        )
