"""Optional OpenAI embeddings provider (stub for future use)."""

from __future__ import annotations

import logging

from app.integrations.embeddings.provider import EmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Structure for future OpenAI integration; requires API key and httpx client."""

    def __init__(self, *, api_key: str, vector_size: int = 384, model: str = "text-embedding-3-small") -> None:
        self._api_key = api_key
        self._vector_size = vector_size
        self._model = model

    @property
    def vector_size(self) -> int:
        return self._vector_size

    async def embed_text(self, text: str) -> list[float]:
        if not self._api_key:
            raise NotImplementedError("OpenAI API key not configured")
        logger.debug("openai_embed_stub", extra={"model": self._model})
        raise NotImplementedError("OpenAIEmbeddingProvider is not implemented yet")

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for text in texts:
            results.append(await self.embed_text(text))
        return results