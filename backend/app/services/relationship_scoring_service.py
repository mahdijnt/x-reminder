"""Relationship strength scoring (structure + mock/heuristic)."""

from __future__ import annotations

from app.core.config import Settings
from app.schemas.ai import RelationshipScore


class RelationshipScoringService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def score_relationship(self, user_id: str, account_id: str) -> RelationshipScore:
        if not self._settings.QDRANT_ENABLED:
            return RelationshipScore(
                user_id=user_id,
                account_id=account_id,
                score=0.35,
                factors={"mock": 1.0},
                source="mock",
            )

        # Future: mutual follow, engagement frequency, topic overlap from Qdrant payloads
        base = 0.5
        if user_id == account_id:
            base = 1.0
        overlap = min(len(user_id), len(account_id)) / max(len(user_id), len(account_id), 1)
        score = round(min(1.0, base * 0.4 + overlap * 0.6), 4)
        return RelationshipScore(
            user_id=user_id,
            account_id=account_id,
            score=score,
            factors={"topic_overlap_proxy": overlap},
            source="heuristic",
        )