"""Qdrant-specific exceptions."""

from typing import Any

from app.core.exceptions import AppException


class QdrantError(AppException):
    def __init__(
        self,
        message: str = "Qdrant error",
        *,
        code: str = "qdrant_error",
        status_code: int = 503,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, code=code, status_code=status_code, **kwargs)


class QdrantConnectionError(QdrantError):
    def __init__(self, message: str = "Qdrant connection failed", **kwargs: Any) -> None:
        super().__init__(
            message,
            code=kwargs.pop("code", "qdrant_connection_error"),
            status_code=503,
            **kwargs,
        )


class QdrantOperationError(QdrantError):
    def __init__(self, message: str = "Qdrant operation failed", **kwargs: Any) -> None:
        super().__init__(
            message,
            code=kwargs.pop("code", "qdrant_operation_error"),
            status_code=503,
            **kwargs,
        )


class QdrantUnavailableError(QdrantError):
    def __init__(self, message: str = "Qdrant is unavailable", **kwargs: Any) -> None:
        super().__init__(
            message,
            code=kwargs.pop("code", "qdrant_unavailable"),
            status_code=503,
            **kwargs,
        )