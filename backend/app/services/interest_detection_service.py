"""User interest extraction from stored tweet memory."""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.repositories.qdrant_repository import QdrantRepository
from app.schemas.ai import InterestProfile
from app.services.topic_detection_service import TopicDetectionService

logger = logging.getLogger(__name__)


class InterestDetectionService:
    def __init__(
        self,
        settings: Settings,
        repository: QdrantRepository,
        topic_service: TopicDetectionService,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._topic_service = topic_service

    async def get_interests(self, user_id: str, *, sample_texts: list[str] | None = None) -> InterestProfile:
        texts = list(sample_texts or [])
        source = "heuristic"

        if not texts and self._settings.QDRANT_ENABLED:
            records = await self._repository.scroll(
                self._settings.QDRANT_COLLECTION_TWEETS,
                limit=40,
                filters=self._repository.build_user_filter(user_id),
            )
            texts = [str(r.get("text", "")) for r in records if r.get("text")]
            if texts:
                source = "qdrant"

        if not texts:
            logger.info("interest_detection_fallback", extra={"user_id": user_id})
            return InterestProfile(user_id=user_id, topics={"general": 1.0}, source="mock")

        topics: dict[str, float] = {}
        for text in texts:
            for topic in await self._topic_service.detect_topics(text):
                topics[topic] = topics.get(topic, 0.0) + 1.0

        total = sum(topics.values()) or 1.0
        normalized = {k: round(v / total, 4) for k, v in topics.items()}
        return InterestProfile(user_id=user_id, topics=normalized, source=source)
