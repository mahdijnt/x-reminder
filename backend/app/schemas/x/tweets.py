"""Tweet schemas."""

from datetime import datetime

from pydantic import BaseModel


class TweetItem(BaseModel):
    tweet_id: str
    author_id: str
    username: str
    text: str
    created_at: datetime
    url: str


class TweetListResponse(BaseModel):
    items: list[TweetItem]
    next_token: str | None = None
