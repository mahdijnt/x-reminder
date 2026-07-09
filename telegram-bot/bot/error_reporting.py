from __future__ import annotations

import logging
from typing import Any

from bot.config import Settings

logger = logging.getLogger(__name__)


def report_exception(settings: Settings, exc: Exception, context: dict[str, Any] | None = None) -> None:
    if settings.error_monitoring_provider == "none" or not settings.error_monitoring_dsn:
        logger.error("bot_error_captured", extra={"error": str(exc), "context": context or {}})
        return
    logger.error("bot_error_captured_external", extra={"provider": settings.error_monitoring_provider, "error": str(exc), "context": context or {}})
