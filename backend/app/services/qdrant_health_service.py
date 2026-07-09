"""Dedicated Qdrant health diagnostics."""

from __future__ import annotations

from app.core.config import Settings
from app.infrastructure.qdrant.connection import QdrantManager
from app.schemas.health import QdrantHealthData


class QdrantHealthService:
    def __init__(self, settings: Settings, qdrant_manager: QdrantManager) -> None:
        self._settings = settings
        self._qdrant_manager = qdrant_manager

    async def get_health(self) -> QdrantHealthData:
        if not self._settings.QDRANT_ENABLED:
            return QdrantHealthData(
                connected=False,
                enabled=False,
                latency_ms=None,
                collections=[],
                detail="QDRANT_ENABLED=false",
            )
        payload = await self._qdrant_manager.health_snapshot()
        return QdrantHealthData(enabled=True, **payload)
