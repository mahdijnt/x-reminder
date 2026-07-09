"""Lightweight app-user identification for backend routes."""

from typing import Annotated

from fastapi import Depends, Header

from app.core.access_tokens import parse_access_token
from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError


async def get_app_user_id(
    x_app_user_id: Annotated[str | None, Header(alias="X-App-User-Id")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    settings: Settings = Depends(get_settings),
) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        try:
            parsed = parse_access_token(authorization, settings.SECRET_KEY)
            return parsed["id"]
        except Exception as exc:
            raise UnauthorizedError("Invalid authorization token") from exc
    if x_app_user_id and x_app_user_id.strip():
        return x_app_user_id.strip()
    raise UnauthorizedError("Missing X-App-User-Id header or Authorization bearer token")


AppUserIdDep = Annotated[str, Depends(get_app_user_id)]
