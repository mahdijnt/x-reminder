"""X API specific exceptions."""

from typing import Any

from app.core.exceptions import AppException


class XAPIError(AppException):
    def __init__(
        self,
        message: str = "X API error",
        *,
        code: str = "x_api_error",
        status_code: int = 502,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, status_code=status_code, details=details or {})


class XAuthError(XAPIError):
    def __init__(self, message: str = "X authentication failed", **kwargs: Any) -> None:
        super().__init__(
            message,
            code=kwargs.pop("code", "x_auth_error"),
            status_code=kwargs.pop("status_code", 401),
            **kwargs,
        )


class XRateLimitError(XAPIError):
    def __init__(
        self,
        message: str = "X API rate limit exceeded",
        *,
        reset_at: int | None = None,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = dict(kwargs.pop("details", None) or {})
        if reset_at is not None:
            details["reset_at"] = reset_at
        if retry_after is not None:
            details["retry_after"] = retry_after
        super().__init__(
            message,
            code=kwargs.pop("code", "x_rate_limit"),
            status_code=429,
            details=details,
            **kwargs,
        )


class XNotFoundError(XAPIError):
    def __init__(self, message: str = "X resource not found", **kwargs: Any) -> None:
        super().__init__(
            message,
            code=kwargs.pop("code", "x_not_found"),
            status_code=404,
            **kwargs,
        )


class XTokenError(XAuthError):
    def __init__(self, message: str = "X token error", **kwargs: Any) -> None:
        super().__init__(message, code=kwargs.pop("code", "x_token_error"), **kwargs)
