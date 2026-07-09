from __future__ import annotations

from typing import Any

from bot.config import Settings
from services.api_client import BackendHttpClient, BackendResponseError, RetryConfig


class HttpApiClient:
    def __init__(self, settings: Settings) -> None:
        self._http = BackendHttpClient(
            base_url=settings.backend_base_url,
            timeout_seconds=settings.api_timeout_seconds,
            retry=RetryConfig(
                max_attempts=settings.api_retry_attempts,
                base_delay_seconds=settings.api_retry_base_delay_seconds,
                max_delay_seconds=settings.api_retry_max_delay_seconds,
            ),
        )

    @staticmethod
    def _data(payload: dict[str, Any]) -> Any:
        if payload.get("success") is not True:
            raise BackendResponseError(payload.get("message", "Backend returned unsuccessful response"))
        if "data" not in payload:
            raise BackendResponseError("Backend response missing data field")
        return payload["data"]

    async def get_user_profile(self, telegram_id: int) -> dict[str, Any]:
        profile = self._data(await self._http.request_json("GET", "/x/profile", telegram_id=telegram_id))
        return {
            "telegram_id": telegram_id,
            "display_name": profile.get("name") or profile.get("username") or str(telegram_id),
            "x_username": profile.get("username"),
            "x_connected": True,
            "locale": "en",
        }

    async def get_dashboard_stats(self, telegram_id: int) -> dict[str, Any]:
        summary = self._data(await self._http.request_json("GET", "/analytics/summary", telegram_id=telegram_id))
        watch_lists = await self.get_watch_lists(telegram_id)
        return {
            "x_connected": True,
            "follow_targets_count": len(watch_lists.get("follow_targets", [])),
            "following_count": len(watch_lists.get("following", [])),
            "mutual_count": len(watch_lists.get("mutual_followers", [])),
            "notifications_unread": 0,
            "targets_achieved_count": 0,
            "success_rate": summary.get("kpis", {}).get("success_rate"),
            "follow_back_rate": summary.get("kpis", {}).get("follow_back_rate"),
        }

    async def _watch_list(self, telegram_id: int, path: str) -> list[dict[str, Any]]:
        data = self._data(await self._http.request_json("GET", path, telegram_id=telegram_id))
        items = data.get("items", [])
        normalized: list[dict[str, Any]] = []
        for item in items:
            normalized.append(
                {
                    "x_user_id": item.get("x_user_id", ""),
                    "username": item.get("username", "unknown"),
                    "display_name": item.get("name") or item.get("username", "unknown"),
                }
            )
        return normalized

    async def get_watch_lists(self, telegram_id: int) -> dict[str, list[dict[str, Any]]]:
        follow_targets, following, mutual = await self.get_follow_targets(telegram_id), await self.get_following(telegram_id), await self.get_mutual_followers(telegram_id)
        return {
            "follow_targets": follow_targets,
            "following": following,
            "mutual_followers": mutual,
        }

    async def get_follow_targets(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._watch_list(telegram_id, "/watch-lists/follow-targets")

    async def get_following(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._watch_list(telegram_id, "/watch-lists/following")

    async def get_mutual_followers(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._watch_list(telegram_id, "/watch-lists/mutual-followers")

    async def add_account(self, telegram_id: int, username: str, list_type: str = "follow_targets") -> dict[str, Any]:
        cleaned = username.lstrip("@").strip()
        if not cleaned:
            return {"ok": False, "error": "invalid_username"}
        payload = {"x_user_id": cleaned, "username": cleaned, "name": cleaned}
        data = self._data(
            await self._http.request_json(
                "POST",
                "/watch-lists/follow-targets",
                telegram_id=telegram_id,
                json_body=payload,
            )
        )
        for item in data.get("items", []):
            if item.get("username", "").lower() == cleaned.lower():
                return {
                    "ok": True,
                    "account": {
                        "username": item.get("username", cleaned),
                        "display_name": item.get("name") or item.get("username", cleaned),
                    },
                }
        return {"ok": True, "account": {"username": cleaned, "display_name": cleaned}}

    async def remove_account(self, telegram_id: int, username: str, list_type: str = "follow_targets") -> dict[str, Any]:
        cleaned = username.lstrip("@").strip()
        current = await self.get_follow_targets(telegram_id)
        match = next((item for item in current if item.get("username", "").lower() == cleaned.lower()), None)
        if not match:
            return {"ok": False, "error": "not_found"}
        await self._http.request_json(
            "DELETE",
            "/watch-lists/follow-targets",
            telegram_id=telegram_id,
            params={"x_user_id": match.get("x_user_id") or cleaned},
        )
        return {"ok": True, "removed": cleaned}

    async def get_notifications(self, telegram_id: int) -> list[dict[str, Any]]:
        data = self._data(await self._http.request_json("GET", "/notifications/history", telegram_id=telegram_id))
        items = data.get("items", [])
        normalized: list[dict[str, Any]] = []
        for item in items:
            normalized.append(
                {
                    "id": item.get("notification_id"),
                    "username": item.get("tweet_id", "unknown"),
                    "tweet_url": "",
                    "text": f"status={item.get('status', 'unknown')}",
                    "posted_at": item.get("sent_at", ""),
                }
            )
        return normalized

    async def get_target_achieved(self, telegram_id: int) -> list[dict[str, Any]]:
        data = self._data(await self._http.request_json("GET", "/notifications/history", telegram_id=telegram_id))
        items = data.get("items", [])
        return [
            {
                "id": item.get("notification_id"),
                "username": item.get("tweet_id", "unknown"),
                "target_type": "notification_sent",
                "achieved_at": item.get("sent_at", ""),
            }
            for item in items
            if item.get("status") == "sent"
        ]

    async def get_settings(self, telegram_id: int) -> dict[str, Any]:
        data = self._data(await self._http.request_json("GET", "/notifications/status", telegram_id=telegram_id))
        return {
            "notifications_enabled": bool(data.get("enabled", False)),
            "worker_enabled": bool(data.get("worker_enabled", False)),
            "telegram_configured": bool(data.get("telegram_configured", False)),
        }

    async def update_settings(self, telegram_id: int, updates: dict[str, Any]) -> dict[str, Any]:
        current = await self.get_settings(telegram_id)
        current.update(updates)
        return current

    async def connect_x(self, telegram_id: int) -> dict[str, Any]:
        data = self._data(
            await self._http.request_json(
                "GET",
                "/x/oauth/authorize",
                telegram_id=telegram_id,
                params={"app_user_id": str(telegram_id)},
            )
        )
        return {
            "ok": True,
            "x_username": "authorized",
            "authorization_url": data.get("authorization_url", ""),
        }
