from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from services.mock_backend import MockBackend


@runtime_checkable
class ApiClient(Protocol):
    async def get_user_profile(self, telegram_id: int) -> dict[str, Any]: ...
    async def get_dashboard_stats(self, telegram_id: int) -> dict[str, Any]: ...
    async def get_watch_lists(self, telegram_id: int) -> dict[str, list[dict[str, Any]]]: ...
    async def get_follow_targets(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def get_following(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def get_mutual_followers(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def add_account(
        self, telegram_id: int, username: str, list_type: str = "follow_targets"
    ) -> dict[str, Any]: ...
    async def remove_account(
        self, telegram_id: int, username: str, list_type: str = "follow_targets"
    ) -> dict[str, Any]: ...
    async def get_notifications(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def get_target_achieved(self, telegram_id: int) -> list[dict[str, Any]]: ...
    async def get_settings(self, telegram_id: int) -> dict[str, Any]: ...
    async def update_settings(
        self, telegram_id: int, updates: dict[str, Any]
    ) -> dict[str, Any]: ...
    async def connect_x(self, telegram_id: int) -> dict[str, Any]: ...


class MockApiClient:
    """ApiClient implementation backed by MockBackend."""

    def __init__(self) -> None:
        self._backend = MockBackend()

    async def get_user_profile(self, telegram_id: int) -> dict[str, Any]:
        return await self._backend.get_user_profile(telegram_id)

    async def get_dashboard_stats(self, telegram_id: int) -> dict[str, Any]:
        return await self._backend.get_dashboard_stats(telegram_id)

    async def get_watch_lists(self, telegram_id: int) -> dict[str, list[dict[str, Any]]]:
        return await self._backend.get_watch_lists(telegram_id)

    async def get_follow_targets(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._backend.get_follow_targets(telegram_id)

    async def get_following(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._backend.get_following(telegram_id)

    async def get_mutual_followers(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._backend.get_mutual_followers(telegram_id)

    async def add_account(
        self, telegram_id: int, username: str, list_type: str = "follow_targets"
    ) -> dict[str, Any]:
        return await self._backend.add_account(telegram_id, username, list_type)

    async def remove_account(
        self, telegram_id: int, username: str, list_type: str = "follow_targets"
    ) -> dict[str, Any]:
        return await self._backend.remove_account(telegram_id, username, list_type)

    async def get_notifications(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._backend.get_notifications(telegram_id)

    async def get_target_achieved(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._backend.get_target_achieved(telegram_id)

    async def get_settings(self, telegram_id: int) -> dict[str, Any]:
        return await self._backend.get_settings(telegram_id)

    async def update_settings(
        self, telegram_id: int, updates: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._backend.update_settings(telegram_id, updates)

    async def connect_x(self, telegram_id: int) -> dict[str, Any]:
        return await self._backend.connect_x(telegram_id)


def create_api_client(use_mock: bool = True, settings: object | None = None) -> ApiClient:
    if use_mock:
        return MockApiClient()
    if settings is None:
        raise ValueError("settings are required when use_mock is False")
    from services.http_backend import HttpApiClient
    return HttpApiClient(settings)
