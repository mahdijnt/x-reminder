"""OAuth endpoint schemas."""

from pydantic import BaseModel, Field


class XOAuthAuthorizeData(BaseModel):
    authorization_url: str
    state: str


class XOAuthCallbackData(BaseModel):
    connected: bool = True
    x_user_id: str | None = None
    username: str | None = None


class XOAuthDisconnectData(BaseModel):
    disconnected: bool = True
