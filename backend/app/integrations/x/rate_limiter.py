"""Parse and track X API rate limit response headers."""

from __future__ import annotations

import logging
from typing import Any

from app.integrations.x.models import XRateLimitInfo

logger = logging.getLogger(__name__)


def parse_rate_limit_headers(headers: dict[str, Any]) -> XRateLimitInfo:
    def _get(name: str) -> int | None:
        raw = headers.get(name) or headers.get(name.lower())
        if raw is None:
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    return XRateLimitInfo(
        limit=_get("x-rate-limit-limit"),
        remaining=_get("x-rate-limit-remaining"),
        reset=_get("x-rate-limit-reset"),
    )


def log_rate_limit(endpoint: str, info: XRateLimitInfo) -> None:
    logger.info(
        "x_api_rate_limit",
        extra={
            "endpoint": endpoint,
            "limit": info.limit,
            "remaining": info.remaining,
            "reset": info.reset,
        },
    )
