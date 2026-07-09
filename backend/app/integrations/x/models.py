"""Pydantic models for X API JSON payloads."""

from datetime import datetime

from pydantic import BaseModel, Field


class XUserData(BaseModel):
    id: str
    name: str
    username: str
    description: str | None = None
    profile_image_url: str | None = None
    public_metrics: dict[str, int] | None = None
    created_at: datetime | None = None


class XUserResponse(BaseModel):
    data: XUserData | None = None


class XUsersListMeta(BaseModel):
    next_token: str | None = None
    result_count: int | None = None


class XUsersListResponse(BaseModel):
    data: list[XUserData] | None = None
    meta: XUsersListMeta | None = None


class XTweetData(BaseModel):
    id: str
    text: str
    author_id: str | None = None
    created_at: datetime | None = None
    conversation_id: str | None = None
    in_reply_to_user_id: str | None = None
    referenced_tweets: list[dict[str, str]] | None = None


class XTweetsListResponse(BaseModel):
    data: list[XTweetData] | None = None
    includes: dict | None = None
    meta: XUsersListMeta | None = None


class XOAuthTokenResponse(BaseModel):
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str | None = None
    scope: str | None = None


class XRateLimitInfo(BaseModel):
    limit: int | None = None
    remaining: int | None = None
    reset: int | None = None


class StoredXTokens(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expires_at: int | None = None
    scope: str | None = None
    x_user_id: str | None = None
    token_type: str = "bearer"
