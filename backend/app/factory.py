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
from app.services.health_service import HealthService

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

    yield

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
