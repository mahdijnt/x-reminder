"""Tweet domain models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, HttpUrl


class FilteredTweet(BaseModel):
    tweet_id: str
    author_id: str
    username: str
    text: str
    created_at: datetime
    url: str


class ProcessedTweetRecord(BaseModel):
    tweet_id: str
    author_id: str
    processed_time: datetime
    notification_status: Literal["pending", "sent", "skipped"] = "pending"
