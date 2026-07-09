"""Health check business service."""

from datetime import datetime, timezone

from app.core.config import Settings
from app.infrastructure.redis.connection import RedisManager
from app.infrastructure.qdrant.connection import QdrantManager
from app.repositories.base import InMemoryRepository
from app.schemas.health import HealthCheckItem, HealthData


class HealthService:
    def __init__(
        self,
        settings: Settings,
        repository: InMemoryRepository,
        redis_manager: RedisManager | None = None,
        monitoring_engine=None,
        notification_engine=None,
        qdrant_manager: QdrantManager | None = None,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._redis_manager = redis_manager
        self._monitoring_engine = monitoring_engine
        self._notification_engine = notification_engine
        self._qdrant_manager = qdrant_manager

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

        if self._settings.x_oauth_configured:
            checks["x_oauth"] = HealthCheckItem(status="configured")
        else:
            checks["x_oauth"] = HealthCheckItem(
                status="missing_config",
                detail="Set X_CLIENT_ID, X_CLIENT_SECRET, and X_CALLBACK_URL",
            )


        if self._settings.MONITORING_ENABLED:
            if self._monitoring_engine is None:
                checks["monitoring"] = HealthCheckItem(status="unavailable", detail="Engine not initialized")
                overall = "degraded" if overall == "ok" else overall
            else:
                status = await self._monitoring_engine.status()
                ok = status.get("scheduler_running") and status.get("worker_running")
                checks["monitoring"] = HealthCheckItem(
                    status="ok" if ok else "degraded",
                    detail=f"queue_depth={status.get('queue_depth', 0)}",
                )
                if not ok:
                    overall = "degraded"
        else:
            checks["monitoring"] = HealthCheckItem(status="disabled", detail="MONITORING_ENABLED=false")




        if self._settings.QDRANT_ENABLED:
            if self._qdrant_manager is None:
                checks["qdrant"] = HealthCheckItem(
                    status="unavailable",
                    detail="Qdrant manager not initialized",
                )
                overall = "degraded"
            else:
                qdrant_ok = await self._qdrant_manager.ping()
                if qdrant_ok:
                    count = self._qdrant_manager.collection_count
                    checks["qdrant"] = HealthCheckItem(
                        status="ok",
                        detail=f"collections={count if count is not None else 'unknown'}",
                    )
                else:
                    checks["qdrant"] = HealthCheckItem(
                        status="unavailable",
                        detail="Qdrant ping failed or not connected",
                    )
                    overall = "degraded"
        else:
            checks["qdrant"] = HealthCheckItem(status="disabled", detail="QDRANT_ENABLED=false")


        if self._settings.ANALYTICS_ENABLED:
            checks["analytics"] = HealthCheckItem(status="ok", detail="analytics APIs enabled")
        else:
            checks["analytics"] = HealthCheckItem(status="disabled", detail="ANALYTICS_ENABLED=false")

        if self._settings.NOTIFICATIONS_ENABLED:
            if self._notification_engine is None:
                checks["notifications"] = HealthCheckItem(status="unavailable", detail="Engine not initialized")
                overall = "degraded" if overall == "ok" else overall
            else:
                status = await self._notification_engine.status()
                ok = status.get("worker_running") or not self._settings.NOTIFICATIONS_WORKER_ENABLED
                checks["notifications"] = HealthCheckItem(
                    status="ok" if ok else "degraded",
                    detail=f"queue_depth={status.get('queue_depth', {})}",
                )
                if not ok:
                    overall = "degraded"
        else:
            checks["notifications"] = HealthCheckItem(status="disabled", detail="NOTIFICATIONS_ENABLED=false")


        return HealthData(
            status=overall,
            version=self._settings.APP_VERSION,
            environment=self._settings.ENVIRONMENT.value,
            timestamp=datetime.now(timezone.utc),
            checks=checks,
        )
