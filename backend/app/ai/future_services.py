"""Placeholders for upcoming AI capabilities."""

from __future__ import annotations


class ReplySuggestionService:
    """Future: generate smart reply suggestions based on tweet context and user voice."""

    async def suggest_replies(self, tweet_text: str, user_id: str) -> list[str]:
        raise NotImplementedError("ReplySuggestionService is not implemented yet")


class AccountClassificationService:
    """Future: classify accounts (bot, influencer, niche expert, etc.)."""

    async def classify(self, account_id: str) -> dict:
        raise NotImplementedError("AccountClassificationService is not implemented yet")


class GrowthRecommendationService:
    """Future: recommend accounts and engagement actions for audience growth."""

    async def recommend_actions(self, user_id: str) -> list[dict]:
        raise NotImplementedError("GrowthRecommendationService is not implemented yet")