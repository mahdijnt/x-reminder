from __future__ import annotations

from typing import Any

import httpx

from bot.config import Settings
from services.api_client import ApiClient


class HttpApiClient(ApiClient):
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.backend_base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=settings.api_timeout_seconds)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = await self._client.get(f"{self._base_url}{path}", params=params)
        response.raise_for_status()
        return response.json()

    async def get_user_profile(self, telegram_id: int) -> dict[str, Any]: return await self._get("/profile", {"telegram_id": telegram_id})
    async def get_dashboard_stats(self, telegram_id: int) -> dict[str, Any]: return await self._get("/dashboard/stats", {"telegram_id": telegram_id})
    async def get_watch_lists(self, telegram_id: int) -> dict[str, list[dict[str, Any]]]: return await self._get("/watch-lists", {"telegram_id": telegram_id})
    async def get_follow_targets(self, telegram_id: int) -> list[dict[str, Any]]: return await self._get("/follow-targets", {"telegram_id": telegram_id})
    async def get_following(self, telegram_id: int) -> list[dict[str, Any]]: return await self._get("/following", {"telegram_id": telegram_id})
    async def get_mutual_followers(self, telegram_id: int) -> list[dict[str, Any]]: return await self._get("/mutual-followers", {"telegram_id": telegram_id})
    async def add_account(self, telegram_id: int, username: str, list_type: str = "follow_targets") -> dict[str, Any]: return {"ok": True, "telegram_id": telegram_id, "username": username, "list_type": list_type}
    async def remove_account(self, telegram_id: int, username: str, list_type: str = "follow_targets") -> dict[str, Any]: return {"ok": True, "telegram_id": telegram_id, "username": username, "list_type": list_type}
    async def get_notifications(self, telegram_id: int) -> list[dict[str, Any]]: return await self._get("/notifications", {"telegram_id": telegram_id})
    async def get_target_achieved(self, telegram_id: int) -> list[dict[str, Any]]: return await self._get("/target-achieved", {"telegram_id": telegram_id})
    async def get_settings(self, telegram_id: int) -> dict[str, Any]: return await self._get("/settings", {"telegram_id": telegram_id})
    async def update_settings(self, telegram_id: int, updates: dict[str, Any]) -> dict[str, Any]: return {"ok": True, "telegram_id": telegram_id, "updates": updates}
    async def connect_x(self, telegram_id: int) -> dict[str, Any]: return await self._get("/connect-x", {"telegram_id": telegram_id})
