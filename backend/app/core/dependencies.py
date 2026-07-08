"""FastAPI dependency injection helpers."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.repositories.base import InMemoryRepository
from app.services.health_service import HealthService

SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_health_repository() -> AsyncGenerator[InMemoryRepository, None]:
    yield InMemoryRepository()


async def get_health_service(
    settings: SettingsDep,
    repository: Annotated[InMemoryRepository, Depends(get_health_repository)],
) -> AsyncGenerator[HealthService, None]:
    yield HealthService(settings=settings, repository=repository)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
