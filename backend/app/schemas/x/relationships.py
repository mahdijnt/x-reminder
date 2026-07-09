"""Followers/following schemas."""

from pydantic import BaseModel


class XUserSummary(BaseModel):
    x_user_id: str
    username: str
    name: str


class PaginatedUsersResponse(BaseModel):
    items: list[XUserSummary]
    next_token: str | None = None
