from __future__ import annotations

from services.api_client import ApiClient


def get_api_client(context) -> ApiClient:
    client = context.application.bot_data.get("api_client")
    if client is None:
        raise RuntimeError("api_client not configured on application")
    return client


def telegram_id(update) -> int:
    user = update.effective_user
    if user is None:
        raise ValueError("missing user")
    return user.id
