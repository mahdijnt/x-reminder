"""Safe JSON serialization for Redis values."""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class RedisSerializationError(ValueError):
    """Raised when a value cannot be serialized for Redis."""


def serialize_json(value: Any) -> str:
    """Serialize nested structures to a JSON string for Redis storage."""
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except (TypeError, ValueError) as exc:
        logger.error(
            "redis_serialize_failed",
            extra={"event": "redis_serialize_failed", "error": str(exc)},
        )
        raise RedisSerializationError(str(exc)) from exc


def deserialize_json(raw: str) -> Any:
    """Deserialize JSON from Redis; raises on invalid payloads."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning(
            "redis_deserialize_failed",
            extra={"event": "redis_deserialize_failed", "error": str(exc)},
        )
        raise RedisSerializationError(str(exc)) from exc


def try_deserialize_json(raw: str) -> Any | None:
    try:
        return deserialize_json(raw)
    except RedisSerializationError:
        return None
