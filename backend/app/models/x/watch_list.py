"""Watch list domain models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class WatchListType(str, Enum):
    FOLLOW_TARGETS = "follow-targets"
    FOLLOWING = "following"
    MUTUAL_FOLLOWERS = "mutual-followers"


class WatchListEntry(BaseModel):
    x_user_id: str
    username: str
    name: str | None = None
    added_at: datetime | None = None
