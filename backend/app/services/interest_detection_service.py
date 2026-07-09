"""Heuristic user interest extraction."""

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
        topics: dict[str, float] = {}
        texts = sample_texts or []
        if not texts:
            logger.info("interest_detection_mock", extra={"user_id": user_id})
            return InterestProfile(user_id=user_id, topics={"general": 1.0}, source="mock")

        for text in texts:
            for topic in await self._topic_service.detect_topics(text):
                topics[topic] = topics.get(topic, 0.0) + 1.0

        total = sum(topics.values()) or 1.0
        normalized = {k: round(v / total, 4) for k, v in topics.items()}
        return InterestProfile(user_id=user_id, topics=normalized, source="heuristic")