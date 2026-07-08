"""Custom application exceptions."""

from typing import Any


class AppException(Exception):
    """Base exception for domain and API errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "app_error",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "not_found"), status_code=404, **kwargs)


class ValidationAppError(AppException):
    def __init__(self, message: str = "Validation failed", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "validation_error"), status_code=422, **kwargs)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "unauthorized"), status_code=401, **kwargs)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Forbidden", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "forbidden"), status_code=403, **kwargs)


class ConflictError(AppException):
    def __init__(self, message: str = "Conflict", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "conflict"), status_code=409, **kwargs)
