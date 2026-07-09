"""Detect topics in tweet text."""

from __future__ import annotations

import re

from app.core.config import Settings
from app.integrations.embeddings.service import EmbeddingsService

_TOPIC_KEYWORDS: dict[str, list[str]] = {
    "crypto": ["bitcoin", "ethereum", "crypto", "web3", "defi", "nft"],
    "tech": ["ai", "software", "programming", "python", "startup", "saas"],
    "sports": ["football", "soccer", "nba", "match", "goal"],
    "news": ["breaking", "report", "election", "policy"],
}


class TopicDetectionService:
    def __init__(self, settings: Settings, embeddings: EmbeddingsService) -> None:
        self._settings = settings
        self._embeddings = embeddings

    async def detect_topics(self, text: str) -> list[str]:
        lowered = text.lower()
        found: list[str] = []
        for topic, keywords in _TOPIC_KEYWORDS.items():
            if any(re.search(rf"\b{re.escape(kw)}\b", lowered) for kw in keywords):
                found.append(topic)
        if found:
            return found
        if not self._settings.QDRANT_ENABLED:
            return ["general"]
        # Future: embedding similarity against topic vectors
        _ = await self._embeddings.embed_text(text)
        return ["general"]