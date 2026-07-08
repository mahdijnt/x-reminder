"""Global FastAPI exception handlers."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.schemas.responses import APIResponse, ErrorDetail

logger = logging.getLogger(__name__)


def _error_body(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = APIResponse.fail(message=message, code=code, details=details)
    return payload.model_dump()


def register_exception_handlers(app: FastAPI) -> None:
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
        return JSONResponse(
            status_code=500,
            content=_error_body("internal_server_error", "An unexpected error occurred"),
        )
