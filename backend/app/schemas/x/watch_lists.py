"""Watch list API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class WatchListEntrySchema(BaseModel):
    x_user_id: str
    username: str
    name: str | None = None
    added_at: datetime | None = None


class WatchListResponse(BaseModel):
    list_type: str
    items: list[WatchListEntrySchema]


class FollowTargetCreateRequest(BaseModel):
    x_user_id: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    name: str | None = None


class WatchListSyncResponse(BaseModel):
    synced: bool = True
    following_count: int = 0
    mutual_followers_count: int = 0
    profile_updated: bool = False
    last_scan_timestamp: int | None = None
