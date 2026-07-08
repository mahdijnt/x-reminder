"""FastAPI dependency injection helpers."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.core.rate_limit import RateLimiter, get_rate_limiter
from app.infrastructure.redis.connection import RedisManager, get_redis_manager
from app.infrastructure.redis.session_store import SessionStore
from app.infrastructure.redis.temp_store import TempStore
from app.infrastructure.redis.user_cache import UserCache
from app.repositories.base import InMemoryRepository
from app.repositories.redis_repository import RedisRepository
from app.services.cache_service import CacheService
from app.services.health_service import HealthService

SettingsDep = Annotated[Settings, Depends(get_settings)]


def _manager_from_request(request: Request) -> RedisManager:
    manager = getattr(request.app.state, "redis_manager", None)
    if manager is not None:
        return manager
    return get_redis_manager()


RedisManagerDep = Annotated[RedisManager, Depends(_manager_from_request)]


async def get_health_repository() -> AsyncGenerator[InMemoryRepository, None]:
    yield InMemoryRepository()


async def get_redis_repository(
    manager: RedisManagerDep,
) -> AsyncGenerator[RedisRepository, None]:
    yield RedisRepository(manager)


async def get_cache_service(
    repository: Annotated[RedisRepository, Depends(get_redis_repository)],
) -> AsyncGenerator[CacheService, None]:
    yield CacheService(repository)


async def get_session_store(
    repository: Annotated[RedisRepository, Depends(get_redis_repository)],
) -> AsyncGenerator[SessionStore, None]:
    yield SessionStore(repository)


async def get_user_cache(
    repository: Annotated[RedisRepository, Depends(get_redis_repository)],
) -> AsyncGenerator[UserCache, None]:
    yield UserCache(repository)


async def get_temp_store(
    repository: Annotated[RedisRepository, Depends(get_redis_repository)],
) -> AsyncGenerator[TempStore, None]:
    yield TempStore(repository)


async def get_health_service(
    settings: SettingsDep,
    repository: Annotated[InMemoryRepository, Depends(get_health_repository)],
    manager: RedisManagerDep,
) -> AsyncGenerator[HealthService, None]:
    yield HealthService(settings=settings, repository=repository, redis_manager=manager)


async def get_rate_limiter_dep(
    settings: SettingsDep,
    manager: RedisManagerDep,
) -> AsyncGenerator[RateLimiter, None]:
    yield get_rate_limiter(settings, redis_manager=manager)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
RedisRepositoryDep = Annotated[RedisRepository, Depends(get_redis_repository)]
CacheServiceDep = Annotated[CacheService, Depends(get_cache_service)]
SessionStoreDep = Annotated[SessionStore, Depends(get_session_store)]
UserCacheDep = Annotated[UserCache, Depends(get_user_cache)]
TempStoreDep = Annotated[TempStore, Depends(get_temp_store)]
RateLimiterDep = Annotated[RateLimiter, Depends(get_rate_limiter_dep)]
