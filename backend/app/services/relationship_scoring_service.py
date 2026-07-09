"""Relationship strength scoring with Qdrant memory persistence."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.core.config import Settings
from app.integrations.embeddings.service import EmbeddingsService
from app.repositories.qdrant_repository import QdrantRepository
from app.schemas.ai import RelationshipScore

logger = logging.getLogger(__name__)


class RelationshipScoringService:
    def __init__(
        self,
        settings: Settings,
        repository: QdrantRepository,
        embeddings: EmbeddingsService,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._embeddings = embeddings

    async def score_relationship(self, user_id: str, account_id: str) -> RelationshipScore:
        if not self._settings.QDRANT_ENABLED:
            return RelationshipScore(
                user_id=user_id,
                account_id=account_id,
                score=0.0,
                factors={},
                source="empty",
            )

        memory = await self._repository.get_by_id(
            self._settings.QDRANT_COLLECTION_ACCOUNTS,
            point_id=f"relationship:{user_id}:{account_id}",
        )
        if memory and memory.get("score") is not None:
            factors = memory.get("factors") or {}
            if isinstance(factors, dict):
                return RelationshipScore(
                    user_id=user_id,
                    account_id=account_id,
                    score=float(memory["score"]),
                    factors={str(k): float(v) for k, v in factors.items()},
                    source="qdrant_memory",
                )

        user_tweets = await self._repository.scroll(
            self._settings.QDRANT_COLLECTION_TWEETS,
            limit=30,
            filters=self._repository.build_user_filter(user_id),
        )
        account = await self._repository.get_by_id(
            self._settings.QDRANT_COLLECTION_ACCOUNTS,
            point_id=f"account:{account_id}",
        )

        factors: dict[str, float] = {}
        score = 0.35

        if user_tweets:
            factors["tweet_samples"] = float(min(len(user_tweets), 30))
            score += min(len(user_tweets) / 60.0, 0.25)

        if account:
            factors["account_profile"] = 1.0
            overlap_text = " ".join(str(t.get("text", "")) for t in user_tweets[:10])
            if overlap_text.strip() and (account.get("bio") or account.get("username")):
                user_vec = await self._embeddings.embed_text(overlap_text[:2000])
                account_text = str(account.get("bio") or account.get("username") or account_id)
                account_vec = await self._embeddings.embed_text(account_text)
                similarity = _cosine_similarity(user_vec, account_vec)
                factors["embedding_similarity"] = round(similarity, 4)
                score = round(min(1.0, score * 0.5 + similarity * 0.5), 4)
            else:
                score = round(min(1.0, score + 0.15), 4)
        else:
            overlap = min(len(user_id), len(account_id)) / max(len(user_id), len(account_id), 1)
            factors["id_overlap_proxy"] = round(overlap, 4)
            score = round(min(1.0, score * 0.6 + overlap * 0.4), 4)

        await self._persist_relationship(user_id, account_id, score=score, factors=factors)
        return RelationshipScore(
            user_id=user_id,
            account_id=account_id,
            score=score,
            factors=factors,
            source="qdrant",
        )

    async def _persist_relationship(
        self,
        user_id: str,
        account_id: str,
        *,
        score: float,
        factors: dict[str, float],
    ) -> None:
        summary = f"relationship user={user_id} account={account_id} score={score}"
        vector = await self._embeddings.embed_text(summary)
        await self._repository.upsert(
            self._settings.QDRANT_COLLECTION_ACCOUNTS,
            point_id=f"relationship:{user_id}:{account_id}",
            vector=vector,
            payload={
                "record_type": "relationship",
                "user_id": user_id,
                "account_id": account_id,
                "score": score,
                "factors": factors,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        logger.info(
            "relationship_memory_stored",
            extra={"event": "relationship_memory_stored", "user_id": user_id, "account_id": account_id},
        )


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))
