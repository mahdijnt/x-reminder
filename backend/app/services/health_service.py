"""Health check business service (infrastructure-only)."""

from datetime import datetime, timezone

from app.core.config import Settings
from app.repositories.base import InMemoryRepository
from app.schemas.health import HealthData


class HealthService:
    def __init__(self, settings: Settings, repository: InMemoryRepository) -> None:
        self._settings = settings
        self._repository = repository

    async def get_health(self) -> HealthData:
        # Repository is injected for DI wiring; no external persistence required.
        _ = await self._repository.list_all()

        return HealthData(
            status="ok",
            version=self._settings.APP_VERSION,
            environment=self._settings.ENVIRONMENT.value,
            timestamp=datetime.now(timezone.utc),
        )
