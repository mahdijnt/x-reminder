"""Exponential backoff retry for transient X API failures."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.core.config import Settings
from app.integrations.x.exceptions import XAPIError, XRateLimitError

logger = logging.getLogger(__name__)

T = TypeVar("T")

RETRYABLE_STATUS = {429, 500, 502, 503, 504}
NON_RETRYABLE_STATUS = {401, 403, 404}


async def with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    settings: Settings,
    operation_name: str = "x_api_request",
) -> T:
    max_attempts = settings.X_RETRY_MAX_ATTEMPTS
    base_delay = settings.X_RETRY_BASE_DELAY
    max_delay = settings.X_RETRY_MAX_DELAY

    for attempt in range(1, max_attempts + 1):
        try:
            return await operation()
        except (XAPIError, XRateLimitError) as exc:
            status = exc.status_code
            if status in NON_RETRYABLE_STATUS:
                raise
            if status not in RETRYABLE_STATUS:
                raise
            if attempt >= max_attempts:
                raise
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            if isinstance(exc, XRateLimitError) and exc.details.get("reset_at"):
                delay = max(delay, float(exc.details["reset_at"]) - __import__("time").time())
            logger.warning(
                "x_api_retry",
                extra={"operation": operation_name, "attempt": attempt, "delay": delay, "error": str(exc)},
            )
            await asyncio.sleep(max(0.0, delay))

    raise RuntimeError("retry loop exhausted")
