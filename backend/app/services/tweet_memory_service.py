"""Tweet embedding storage and similarity search."""

from __future__ import annotations

import logging
from datetime import datetime

from app.core.config import Settings
from app.integrations.embeddings.service import EmbeddingsService
from app.repositories.qdrant_repository import QdrantRepository
from app.schemas.ai import SearchHit, SearchType, TweetStoreRequest

logger = logging.getLogger(__name__)


class TweetMemoryService:
    def __init__(
        self,
        settings: Settings,
        repository: QdrantRepository,
        embeddings: EmbeddingsService,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._embeddings = embeddings

    async def store_tweet(self, tweet: TweetStoreRequest) -> None:
        if not self._settings.QDRANT_ENABLED:
            logger.debug("tweet_memory_skipped_disabled", extra={"tweet_id": tweet.tweet_id})
            return

        vector = await self._embeddings.embed_text(tweet.text)
        created_at = tweet.created_at.isoformat() if tweet.created_at else datetime.utcnow().isoformat()
        await self._repository.upsert(
            self._settings.QDRANT_COLLECTION_TWEETS,
            point_id=f"tweet:{tweet.tweet_id}",
            vector=vector,
            payload={
                "tweet_id": tweet.tweet_id,
                "user_id": tweet.user_id,
                "text": tweet.text,
                "created_at": created_at,
                "username": tweet.username,
            },
        )

    async def search_similar_tweets(self, query: str, *, user_id: str | None = None, limit: int = 10) -> list[SearchHit]:
        if not self._settings.QDRANT_ENABLED:
            return []

        vector = await self._embeddings.embed_text(query)
        hits = await self._repository.search(
            self._settings.QDRANT_COLLECTION_TWEETS,
            vector=vector,
            limit=limit,
            filters=self._repository.build_user_filter(user_id),
        )
        return [
            SearchHit(
                type=SearchType.TWEETS,
                id=str(h.get("tweet_id", h.get("id", ""))),
                score=float(h.get("score", 0.0)),
                title=str(h.get("username") or h.get("tweet_id") or ""),
                text=str(h.get("text", "")),
                payload={k: v for k, v in h.items() if k != "score"},
            )
            for h in hits
        ]