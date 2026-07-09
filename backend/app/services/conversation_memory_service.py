"""Per-session conversation context in Qdrant."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from app.core.config import Settings
from app.integrations.embeddings.service import EmbeddingsService
from app.repositories.qdrant_repository import QdrantRepository

logger = logging.getLogger(__name__)


class ConversationMemoryService:
    def __init__(
        self,
        settings: Settings,
        repository: QdrantRepository,
        embeddings: EmbeddingsService,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._embeddings = embeddings

    async def upsert_message(self, session_id: str, role: str, content: str) -> None:
        if not self._settings.QDRANT_ENABLED:
            return

        existing = await self.get_recent_context(session_id, limit=50)
        messages = list(existing.get("messages", []))
        messages.append({"role": role, "content": content, "at": datetime.now(timezone.utc).isoformat()})
        text_blob = "\n".join(f"{m['role']}: {m['content']}" for m in messages[-20:])
        vector = await self._embeddings.embed_text(text_blob)
        await self._repository.upsert(
            self._settings.QDRANT_COLLECTION_CONVERSATIONS,
            point_id=f"session:{session_id}",
            vector=vector,
            payload={
                "session_id": session_id,
                "messages": messages[-50:],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    async def get_recent_context(self, session_id: str, *, limit: int = 20) -> dict:
        if not self._settings.QDRANT_ENABLED:
            return {"session_id": session_id, "messages": [], "mock": True}

        record = await self._repository.get_by_id(
            self._settings.QDRANT_COLLECTION_CONVERSATIONS,
            point_id=f"session:{session_id}",
        )
        if not record:
            return {"session_id": session_id, "messages": []}
        messages = record.get("messages") or []
        if isinstance(messages, str):
            try:
                messages = json.loads(messages)
            except json.JSONDecodeError:
                messages = []
        return {"session_id": session_id, "messages": messages[-limit:]}

    async def clear_session(self, session_id: str) -> None:
        if not self._settings.QDRANT_ENABLED:
            return
        await self._repository.delete(
            self._settings.QDRANT_COLLECTION_CONVERSATIONS,
            point_id=f"session:{session_id}",
        )