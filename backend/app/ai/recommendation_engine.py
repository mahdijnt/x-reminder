"""Recommendation engine interface (stub implementation)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RecommendationEngine(ABC):
    @abstractmethod
    async def recommend(self, user_id: str, *, limit: int = 10) -> list[dict[str, Any]]:
        """Return ranked recommendations for a user."""


class StubRecommendationEngine(RecommendationEngine):
    async def recommend(self, user_id: str, *, limit: int = 10) -> list[dict[str, Any]]:
        return []