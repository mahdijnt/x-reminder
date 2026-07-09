"""Unified semantic + keyword search."""

from __future__ import annotations

import re

from app.core.config import Settings
from app.schemas.ai import SearchResponse, SearchType
from app.services.semantic_search_service import SemanticSearchService
from app.services.topic_detection_service import TopicDetectionService


class SmartSearchService:
    def __init__(
        self,
        settings: Settings,
        semantic: SemanticSearchService,
        topic_service: TopicDetectionService,
    ) -> None:
        self._settings = settings
        self._semantic = semantic
        self._topic_service = topic_service

    async def search(
        self,
        query: str,
        *,
        search_type: SearchType = SearchType.ALL,
        user_id: str | None = None,
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> SearchResponse:
        hits = []
        topics: list[str] = []

        if search_type in (SearchType.TWEETS, SearchType.ALL):
            hits.extend(
                await self._semantic.search_tweets(
                    query,
                    user_id=user_id,
                    limit=limit,
                    score_threshold=score_threshold,
                )
            )
        if search_type in (SearchType.ACCOUNTS, SearchType.ALL):
            hits.extend(
                await self._semantic.search_accounts(
                    query,
                    limit=limit,
                    score_threshold=score_threshold,
                )
            )

        if not hits and query.strip():
            hits = self._keyword_fallback(query, search_type, limit)

        topics = await self._topic_service.detect_topics(query)
        return SearchResponse(query=query, type=search_type, hits=hits[:limit], topics=topics)

    def _keyword_fallback(self, query: str, search_type: SearchType, limit: int):
        from app.schemas.ai import SearchHit

        tokens = [t for t in re.split(r"\\W+", query.lower()) if t]
        text = " ".join(tokens) or query
        hit = SearchHit(
            type=search_type if search_type != SearchType.ALL else SearchType.TWEETS,
            id="keyword-fallback",
            score=0.1,
            title="keyword",
            text=f"Keyword fallback match: {text}",
            payload={"keyword_fallback": True},
        )
        return [hit][:limit]