"""Lightweight app-user identification for backend routes."""

from typing import Annotated

from fastapi import Depends, Header

from app.core.exceptions import UnauthorizedError


async def get_app_user_id(
    x_app_user_id: Annotated[str | None, Header(alias="X-App-User-Id")] = None,
) -> str:
    if not x_app_user_id or not x_app_user_id.strip():
        raise UnauthorizedError("Missing X-App-User-Id header")
    return x_app_user_id.strip()


AppUserIdDep = Annotated[str, Depends(get_app_user_id)]
