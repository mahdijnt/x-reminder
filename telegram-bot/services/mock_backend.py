from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MockStore:
    profiles: dict[int, dict[str, Any]] = field(default_factory=dict)
    watch_lists: dict[int, dict[str, list[dict[str, Any]]]] = field(default_factory=dict)
    settings: dict[int, dict[str, Any]] = field(default_factory=dict)
    notifications: dict[int, list[dict[str, Any]]] = field(default_factory=dict)
    targets_achieved: dict[int, list[dict[str, Any]]] = field(default_factory=dict)
    x_connected: dict[int, bool] = field(default_factory=dict)


_STORE = MockStore()


def _default_profile(telegram_id: int) -> dict[str, Any]:
    return {
        "telegram_id": telegram_id,
        "display_name": f"User {telegram_id}",
        "x_username": None,
        "x_connected": False,
        "locale": "en",
        "created_at": _now_iso(),
    }


def _default_settings() -> dict[str, Any]:
    return {
        "notifications_enabled": True,
        "digest_enabled": False,
        "quiet_hours_start": None,
        "quiet_hours_end": None,
        "locale": "en",
    }


def _seed_lists(telegram_id: int) -> dict[str, list[dict[str, Any]]]:
    return {
        "follow_targets": [
            {"username": "elonmusk", "display_name": "Elon Musk", "followers": 200_000_000},
            {"username": "naval", "display_name": "Naval", "followers": 2_000_000},
        ],
        "following": [
            {"username": "paulg", "display_name": "Paul Graham", "followers": 1_500_000},
        ],
        "mutual_followers": [
            {"username": "friend_dev", "display_name": "Friend Dev", "followers": 12_000},
        ],
    }


def _ensure_user(telegram_id: int) -> None:
    if telegram_id not in _STORE.profiles:
        _STORE.profiles[telegram_id] = _default_profile(telegram_id)
    if telegram_id not in _STORE.watch_lists:
        _STORE.watch_lists[telegram_id] = _seed_lists(telegram_id)
    if telegram_id not in _STORE.settings:
        _STORE.settings[telegram_id] = _default_settings()
    if telegram_id not in _STORE.notifications:
        _STORE.notifications[telegram_id] = [
            {
                "id": "n1",
                "username": "naval",
                "tweet_url": "https://x.com/naval/status/1234567890",
                "text": "Seek wealth, not money or status.",
                "posted_at": _now_iso(),
            }
        ]
    if telegram_id not in _STORE.targets_achieved:
        _STORE.targets_achieved[telegram_id] = [
            {
                "id": "t1",
                "username": "elonmusk",
                "target_type": "follow_back",
                "achieved_at": _now_iso(),
            }
        ]
    if telegram_id not in _STORE.x_connected:
        _STORE.x_connected[telegram_id] = False


class MockBackend:
    """In-memory fake API for development and tests."""

    async def get_user_profile(self, telegram_id: int) -> dict[str, Any]:
        _ensure_user(telegram_id)
        profile = copy.deepcopy(_STORE.profiles[telegram_id])
        profile["x_connected"] = _STORE.x_connected.get(telegram_id, False)
        if profile["x_connected"]:
            profile["x_username"] = profile.get("x_username") or "mock_x_user"
        return profile

    async def get_dashboard_stats(self, telegram_id: int) -> dict[str, Any]:
        _ensure_user(telegram_id)
        lists = _STORE.watch_lists[telegram_id]
        return {
            "follow_targets_count": len(lists["follow_targets"]),
            "following_count": len(lists["following"]),
            "mutual_count": len(lists["mutual_followers"]),
            "notifications_unread": len(_STORE.notifications[telegram_id]),
            "targets_achieved_count": len(_STORE.targets_achieved[telegram_id]),
            "x_connected": _STORE.x_connected.get(telegram_id, False),
            "updated_at": _now_iso(),
        }

    async def get_watch_lists(self, telegram_id: int) -> dict[str, list[dict[str, Any]]]:
        _ensure_user(telegram_id)
        return copy.deepcopy(_STORE.watch_lists[telegram_id])

    async def get_follow_targets(self, telegram_id: int) -> list[dict[str, Any]]:
        data = await self.get_watch_lists(telegram_id)
        return data["follow_targets"]

    async def get_following(self, telegram_id: int) -> list[dict[str, Any]]:
        data = await self.get_watch_lists(telegram_id)
        return data["following"]

    async def get_mutual_followers(self, telegram_id: int) -> list[dict[str, Any]]:
        data = await self.get_watch_lists(telegram_id)
        return data["mutual_followers"]

    async def add_account(
        self, telegram_id: int, username: str, list_type: str = "follow_targets"
    ) -> dict[str, Any]:
        _ensure_user(telegram_id)
        username = username.lstrip("@").strip().lower()
        if not username:
            return {"ok": False, "error": "invalid_username"}
        lists = _STORE.watch_lists[telegram_id]
        bucket = lists.get(list_type, lists["follow_targets"])
        if any(a["username"] == username for a in bucket):
            return {"ok": False, "error": "already_exists"}
        entry = {
            "username": username,
            "display_name": username.title(),
            "followers": 10_000,
        }
        bucket.append(entry)
        return {"ok": True, "account": entry}

    async def remove_account(
        self, telegram_id: int, username: str, list_type: str = "follow_targets"
    ) -> dict[str, Any]:
        _ensure_user(telegram_id)
        username = username.lstrip("@").strip().lower()
        lists = _STORE.watch_lists[telegram_id]
        bucket = lists.get(list_type, lists["follow_targets"])
        before = len(bucket)
        lists[list_type] = [a for a in bucket if a["username"] != username]
        removed = before - len(lists[list_type])
        if removed == 0:
            return {"ok": False, "error": "not_found"}
        return {"ok": True, "removed": username}

    async def get_notifications(self, telegram_id: int) -> list[dict[str, Any]]:
        _ensure_user(telegram_id)
        return copy.deepcopy(_STORE.notifications[telegram_id])

    async def get_target_achieved(self, telegram_id: int) -> list[dict[str, Any]]:
        _ensure_user(telegram_id)
        return copy.deepcopy(_STORE.targets_achieved[telegram_id])

    async def get_settings(self, telegram_id: int) -> dict[str, Any]:
        _ensure_user(telegram_id)
        return copy.deepcopy(_STORE.settings[telegram_id])

    async def update_settings(
        self, telegram_id: int, updates: dict[str, Any]
    ) -> dict[str, Any]:
        _ensure_user(telegram_id)
        current = _STORE.settings[telegram_id]
        current.update({k: v for k, v in updates.items() if k in current or k == "locale"})
        return copy.deepcopy(current)

    async def connect_x(self, telegram_id: int) -> dict[str, Any]:
        _ensure_user(telegram_id)
        _STORE.x_connected[telegram_id] = True
        _STORE.profiles[telegram_id]["x_username"] = "mock_x_user"
        return {
            "ok": True,
            "message": "X account connected (mock OAuth).",
            "x_username": "mock_x_user",
        }
