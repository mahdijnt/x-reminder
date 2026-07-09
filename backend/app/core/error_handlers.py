"""Global FastAPI exception handlers."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.integrations.x.exceptions import XAPIError, XRateLimitError
from app.infrastructure.qdrant.exceptions import QdrantError
from app.schemas.responses import APIResponse, ErrorDetail
from app.core.config import get_settings
from app.monitoring.error_reporter import ErrorReporter

logger = logging.getLogger(__name__)
error_reporter = ErrorReporter(get_settings())


def _error_body(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = APIResponse.fail(message=message, code=code, details=details)
    return payload.model_dump(mode="json")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(XRateLimitError)
    async def x_rate_limit_handler(_request: Request, exc: XRateLimitError) -> JSONResponse:
        logger.warning("x_rate_limit_exceeded", extra={"details": exc.details})
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(XAPIError)
    async def x_api_error_handler(_request: Request, exc: XAPIError) -> JSONResponse:
        logger.warning("x_api_error", extra={"code": exc.code, "status": exc.status_code, "details": exc.details})
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )


    @app.exception_handler(QdrantError)
    async def qdrant_error_handler(_request: Request, exc: QdrantError) -> JSONResponse:
        logger.warning("qdrant_error", extra={"code": exc.code, "details": exc.details})
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        logger.warning("app_exception", extra={"code": exc.code, "status": exc.status_code})
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body("http_error", detail),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            ErrorDetail(
                field=".".join(str(loc) for loc in err.get("loc", [])),
                message=str(err.get("msg", "Invalid value")),
                code=str(err.get("type", "validation_error")),
            ).model_dump()
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_error_body(
                "request_validation_error",
                "Request validation failed",
                {"errors": errors},
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", exc_info=exc)
        error_reporter.capture_exception(exc, context={"scope": "fastapi_unhandled"})
        return JSONResponse(
            status_code=500,
            content=_error_body("internal_server_error", "An unexpected error occurred"),
        )
