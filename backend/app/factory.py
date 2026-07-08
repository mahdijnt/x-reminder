"""FastAPI application factory."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware import RequestIDMiddleware, SecurityHeadersMiddleware, TimingMiddleware
from app.repositories.base import InMemoryRepository
from app.schemas.health import HealthData
from app.schemas.responses import APIResponse
from app.services.health_service import HealthService


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings)
    yield


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
        service = HealthService(settings=settings, repository=InMemoryRepository())
        data = await service.get_health()
        return APIResponse.ok(data=data, message="Service is healthy")

    app.state.settings = settings
    app.state.version = __version__

    return app
