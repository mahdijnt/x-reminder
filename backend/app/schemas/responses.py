"""Standard API response envelope."""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    code: str = "error"


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    code: str = "ok"
    data: T | None = None
    errors: list[ErrorDetail] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def ok(cls, data: T, *, message: str = "OK", code: str = "ok") -> "APIResponse[T]":
        return cls(success=True, message=message, code=code, data=data)

    @classmethod
    def fail(
        cls,
        *,
        message: str,
        code: str = "error",
        details: dict[str, Any] | None = None,
    ) -> "APIResponse[None]":
        errors = None
        if details and "errors" in details:
            errors = [ErrorDetail(**item) for item in details["errors"]]
        return cls(success=False, message=message, code=code, data=None, errors=errors)
