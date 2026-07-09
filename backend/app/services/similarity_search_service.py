"""Unified similarity search for tweets and accounts."""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.integrations.embeddings.service import EmbeddingsService
from app.repositories.qdrant_repository import QdrantRepository
from app.schemas.ai import SearchHit, SearchType, SimilarityResponse
from app.services.tweet_memory_service import TweetMemoryService

logger = logging.getLogger(__name__)


class SimilaritySearchService:
    def __init__(
        self,
        settings: Settings,
        repository: QdrantRepository,
        embeddings: EmbeddingsService,
        tweet_memory: TweetMemoryService,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._embeddings = embeddings
        self._tweet_memory = tweet_memory

    async def find_similar(
        self,
        query: str,
        *,
        target: SearchType = SearchType.TWEETS,
        user_id: str | None = None,
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> SimilarityResponse:
        if target == SearchType.ACCOUNTS:
            hits = await self._similar_accounts(query, limit=limit, score_threshold=score_threshold)
        else:
            hits = await self._tweet_memory.search_similar_tweets(
                query,
                user_id=user_id,
                limit=limit,
            )
            if score_threshold is not None:
                hits = [h for h in hits if h.score >= score_threshold]

        return SimilarityResponse(query=query, target=target, hits=hits)

    async def _similar_accounts(
        self,
        query: str,
        *,
        limit: int,
        score_threshold: float | None,
    ) -> list[SearchHit]:
        if not self._settings.QDRANT_ENABLED:
            return [
                SearchHit(
                    type=SearchType.ACCOUNTS,
                    id="mock-account",
                    score=0.4,
                    title="mock",
                    text=f"Similar mock account for {query}",
                    payload={"mock": True},
                )
            ]

        vector = await self._embeddings.embed_text(query)
        hits = await self._repository.search(
            self._settings.QDRANT_COLLECTION_ACCOUNTS,
            vector=vector,
            limit=limit,
            score_threshold=score_threshold,
        )
        return [
            SearchHit(
                type=SearchType.ACCOUNTS,
                id=str(h.get("user_id", h.get("id", ""))),
                score=float(h.get("score", 0.0)),
                title=str(h.get("username") or h.get("user_id") or ""),
                text=str(h.get("bio", "")),
                payload={k: v for k, v in h.items() if k != "score"},
            )
            for h in hits
        ]
