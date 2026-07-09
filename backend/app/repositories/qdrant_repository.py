"""Vector storage repository backed by Qdrant."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from qdrant_client.http import models as qmodels

from app.core.config import Settings
from app.infrastructure.qdrant.connection import QdrantManager
from app.infrastructure.qdrant.exceptions import QdrantUnavailableError

logger = logging.getLogger(__name__)


class QdrantRepository:
  def __init__(self, settings: Settings, manager: QdrantManager) -> None:
    self._settings = settings
    self._manager = manager

  @property
  def available(self) -> bool:
    return self._settings.QDRANT_ENABLED and self._manager.is_connected

  async def upsert(
    self,
    collection: str,
    *,
    point_id: str,
    vector: list[float],
    payload: dict[str, Any],
  ) -> None:
    if not self._settings.QDRANT_ENABLED:
      return

    async def _op(client):
      await client.upsert(
        collection_name=collection,
        points=[
          qmodels.PointStruct(id=_point_uuid(point_id), vector=vector, payload=payload),
        ],
        wait=True,
      )

    await self._manager.execute(_op)
    logger.info(
      "qdrant_upsert",
      extra={"event": "qdrant_upsert", "collection": collection, "point_id": point_id},
    )

  async def search(
    self,
    collection: str,
    *,
    vector: list[float],
    limit: int = 10,
    score_threshold: float | None = None,
    filters: qmodels.Filter | None = None,
  ) -> list[dict[str, Any]]:
    if not self._settings.QDRANT_ENABLED:
      return []

    async def _op(client):
      return await client.search(
        collection_name=collection,
        query_vector=vector,
        limit=limit,
        score_threshold=score_threshold,
        query_filter=filters,
        with_payload=True,
      )

    try:
      hits = await self._manager.execute(_op)
    except QdrantUnavailableError:
      return []

    results: list[dict[str, Any]] = []
    for hit in hits:
      payload = dict(hit.payload or {})
      payload["score"] = hit.score
      payload["id"] = str(hit.id)
      results.append(payload)
    return results

  async def delete(self, collection: str, *, point_id: str) -> None:
    if not self._settings.QDRANT_ENABLED:
      return

    async def _op(client):
      await client.delete(
        collection_name=collection,
        points_selector=qmodels.PointIdsList(points=[_point_uuid(point_id)]),
        wait=True,
      )

    await self._manager.execute(_op)

  async def get_by_id(self, collection: str, *, point_id: str) -> dict[str, Any] | None:
    if not self._settings.QDRANT_ENABLED:
      return None

    async def _op(client):
      points = await client.retrieve(
        collection_name=collection,
        ids=[_point_uuid(point_id)],
        with_payload=True,
        with_vectors=False,
      )
      return points

    try:
      points = await self._manager.execute(_op)
    except QdrantUnavailableError:
      return None
    if not points:
      return None
    point = points[0]
    payload = dict(point.payload or {})
    payload["id"] = str(point.id)
    return payload

  def build_user_filter(self, user_id: str | None) -> qmodels.Filter | None:
    if not user_id:
      return None
    return qmodels.Filter(
      must=[
        qmodels.FieldCondition(
          key="user_id",
          match=qmodels.MatchValue(value=user_id),
        )
      ]
    )

  def build_date_range_filter(
    self,
    *,
    field: str,
    start: datetime | None,
    end: datetime | None,
  ) -> qmodels.Filter | None:
    conditions: list[qmodels.FieldCondition] = []
    if start is not None:
      conditions.append(
        qmodels.FieldCondition(key=field, range=qmodels.Range(gte=start.isoformat()))
      )
    if end is not None:
      conditions.append(
        qmodels.FieldCondition(key=field, range=qmodels.Range(lte=end.isoformat()))
      )
    if not conditions:
      return None
    return qmodels.Filter(must=conditions)


def _point_uuid(point_id: str) -> str:
  return str(uuid.uuid5(uuid.NAMESPACE_URL, point_id))