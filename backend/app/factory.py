"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.infrastructure.redis.connection import get_redis_manager
from app.middleware import RequestIDMiddleware, SecurityHeadersMiddleware, TimingMiddleware
from app.repositories.base import InMemoryRepository
from app.schemas.health import HealthData
from app.schemas.responses import APIResponse
from app.repositories.redis_repository import RedisRepository
from app.repositories.x_profile_repository import XProfileRepository
from app.repositories.x_watch_list_repository import WatchListRepository
from app.scheduler.x_sync_jobs import XSyncScheduler
from app.services.health_service import HealthService
from app.services.x_profile_service import XProfileService
from app.services.x_relationship_service import XRelationshipService
from app.services.x_sync_service import XSyncService
from app.services.x_token_service import XTokenService
from app.infrastructure.x.rate_limit_state import XRateLimitStateStore
from app.infrastructure.x.token_store import XTokenStore

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings)

    redis_manager = get_redis_manager(settings)
    app.state.redis_manager = redis_manager

    try:
        await redis_manager.connect()
    except Exception as exc:
        logger.warning(
            "redis_startup_connect_failed",
            extra={"error": str(exc)},
        )

    sync_scheduler = None
    monitoring_engine = None
    if settings.X_SYNC_SCHEDULER_ENABLED:
        repository = RedisRepository(redis_manager)
        token_store = XTokenStore(repository, settings)
        token_service = XTokenService(settings, token_store)
        rate_limit_store = XRateLimitStateStore(repository)
        profile_repo = XProfileRepository(repository)
        watch_repo = WatchListRepository(repository)
        profile_service = XProfileService(settings, token_service, profile_repo, rate_limit_store)
        relationship_service = XRelationshipService(settings, token_service, rate_limit_store)
        sync_service = XSyncService(
            settings,
            token_service,
            profile_service,
            relationship_service,
            profile_repo,
            watch_repo,
        )
        sync_scheduler = XSyncScheduler(settings, sync_service)
        sync_scheduler.start()
        app.state.x_sync_scheduler = sync_scheduler

    if settings.MONITORING_ENABLED:
        from app.monitoring.monitoring_engine import MonitoringEngine
        from app.repositories.redis_repository import RedisRepository

        monitoring_engine = MonitoringEngine(settings, RedisRepository(redis_manager))
        monitoring_engine.start()
        app.state.monitoring_engine = monitoring_engine


    yield

    if sync_scheduler is not None:
        sync_scheduler.shutdown()

    if monitoring_engine is not None:
        await monitoring_engine.shutdown()


    await redis_manager.disconnect()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure the FastAPI application."""

    settings = settings or get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="x-reminder backend API foundation",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/healthz", response_model=APIResponse[HealthData], tags=["health"])
    async def healthz() -> APIResponse[HealthData]:
        redis_manager = get_redis_manager(settings)
        service = HealthService(
            settings=settings,
            repository=InMemoryRepository(),
            redis_manager=redis_manager,
        )
        data = await service.get_health()
        message = "Service is healthy" if data.status == "ok" else "Service is degraded"
        return APIResponse.ok(data=data, message=message)

    app.state.settings = settings
    app.state.version = __version__

    return app
