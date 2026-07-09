"""X user domain models."""

from datetime import datetime

from pydantic import BaseModel, Field


class XProfile(BaseModel):
    x_user_id: str
    username: str
    name: str
    description: str | None = None
    profile_image_url: str | None = None
    followers_count: int | None = None
    following_count: int | None = None
    tweet_count: int | None = None
    synced_at: datetime | None = None
