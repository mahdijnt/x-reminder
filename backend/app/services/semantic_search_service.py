"""Semantic vector search over tweets and accounts."""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.integrations.embeddings.service import EmbeddingsService
from app.repositories.qdrant_repository import QdrantRepository
from app.schemas.ai import SearchHit, SearchType

logger = logging.getLogger(__name__)


class SemanticSearchService:
    def __init__(
        self,
        settings: Settings,
        repository: QdrantRepository,
        embeddings: EmbeddingsService,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._embeddings = embeddings

    async def search_tweets(
        self,
        query: str,
        *,
        user_id: str | None = None,
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[SearchHit]:
        if not self._settings.QDRANT_ENABLED:
            return self._mock_hits(query, SearchType.TWEETS, limit)

        vector = await self._embeddings.embed_text(query)
        filters = self._repository.build_user_filter(user_id)
        hits = await self._repository.search(
            self._settings.QDRANT_COLLECTION_TWEETS,
            vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            filters=filters,
        )
        return [self._to_hit(h, SearchType.TWEETS) for h in hits]

    async def search_accounts(
        self,
        query: str,
        *,
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[SearchHit]:
        if not self._settings.QDRANT_ENABLED:
            return self._mock_hits(query, SearchType.ACCOUNTS, limit)

        vector = await self._embeddings.embed_text(query)
        hits = await self._repository.search(
            self._settings.QDRANT_COLLECTION_ACCOUNTS,
            vector=vector,
            limit=limit,
            score_threshold=score_threshold,
        )
        return [self._to_hit(h, SearchType.ACCOUNTS) for h in hits]

    def _to_hit(self, payload: dict, hit_type: SearchType) -> SearchHit:
        return SearchHit(
            type=hit_type,
            id=str(payload.get("tweet_id") or payload.get("user_id") or payload.get("id", "")),
            score=float(payload.get("score", 0.0)),
            title=str(payload.get("username") or payload.get("tweet_id") or payload.get("user_id") or ""),
            text=str(payload.get("text") or payload.get("bio") or ""),
            payload={k: v for k, v in payload.items() if k not in {"score"}},
        )

    def _mock_hits(self, query: str, hit_type: SearchType, limit: int) -> list[SearchHit]:
        logger.info("semantic_search_mock", extra={"query": query, "type": hit_type.value})
        return [
            SearchHit(
                type=hit_type,
                id=f"mock-{hit_type.value}-1",
                score=0.42,
                title="mock-result",
                text=f"Mock semantic match for: {query}",
                payload={"mock": True},
            )
        ][:limit]