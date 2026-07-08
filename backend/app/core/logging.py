"""Structured logging configuration."""

import logging
import sys
from typing import Any

from app.core.config import Settings


class RequestContextFilter(logging.Filter):
    """Attach request-scoped context to log records when present."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def configure_logging(settings: Settings) -> None:
    """Configure application-wide logging."""

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.addFilter(RequestContextFilter())

    if settings.LOG_JSON:
        formatter = logging.Formatter(
            '{"level":"%(levelname)s","logger":"%(name)s","message":"%(message)s",'
            '"request_id":"%(request_id)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | request_id=%(request_id)s | %(message)s"
        )

    handler.setFormatter(formatter)
    root.addHandler(handler)

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def bind_request_context(logger: logging.Logger, **context: Any) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logger, extra=context)
