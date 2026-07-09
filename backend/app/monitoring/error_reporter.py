"""Pluggable error reporting abstraction."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings

logger = logging.getLogger(__name__)


class ErrorReporter:
    def __init__(self, settings: Settings) -> None:
        self._provider = settings.ERROR_MONITORING_PROVIDER.lower()
        self._dsn = settings.ERROR_MONITORING_DSN

    def capture_exception(self, exc: Exception, *, context: dict[str, Any] | None = None) -> None:
        if self._provider == "none" or not self._dsn:
            logger.error("error_captured", extra={"error": str(exc), "context": context or {}})
            return

        logger.error(
            "error_captured_external",
            extra={"provider": self._provider, "error": str(exc), "context": context or {}},
        )
