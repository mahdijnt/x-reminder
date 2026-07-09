"""AI / vector search API schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SearchType(str, Enum):
    TWEETS = "tweets"
    ACCOUNTS = "accounts"
    ALL = "all"


class SearchHit(BaseModel):
    type: SearchType
    id: str
    score: float = 0.0
    title: str = ""
    text: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    type: SearchType
    hits: list[SearchHit] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


class InterestProfile(BaseModel):
    user_id: str
    topics: dict[str, float] = Field(default_factory=dict)
    source: str = "mock"


class TopicResult(BaseModel):
    text: str
    topics: list[str] = Field(default_factory=list)


class RelationshipScore(BaseModel):
    user_id: str
    account_id: str
    score: float
    factors: dict[str, float] = Field(default_factory=dict)
    source: str = "mock"


class TweetStoreRequest(BaseModel):
    tweet_id: str
    user_id: str
    text: str
    username: str | None = None
    created_at: datetime | None = None


class RecommendationsResponse(BaseModel):
    user_id: str
    items: list[dict[str, Any]] = Field(default_factory=list)
    source: str = "stub"