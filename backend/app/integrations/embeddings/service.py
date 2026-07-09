"""Embeddings service facade."""

from __future__ import annotations

from app.core.config import Settings
from app.integrations.embeddings.mock_provider import MockEmbeddingProvider
from app.integrations.embeddings.provider import EmbeddingProvider


class EmbeddingsService:
    def __init__(self, settings: Settings, provider: EmbeddingProvider | None = None) -> None:
        self._settings = settings
        self._provider = provider or MockEmbeddingProvider(settings.QDRANT_VECTOR_SIZE)

    @property
    def vector_size(self) -> int:
        return self._provider.vector_size

    async def embed_text(self, text: str) -> list[float]:
        return await self._provider.embed_text(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return await self._provider.embed_batch(texts)