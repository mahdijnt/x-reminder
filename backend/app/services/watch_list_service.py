"""Watch list management backed by Redis."""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.x.watch_list import WatchListEntry, WatchListType
from app.repositories.x_watch_list_repository import WatchListRepository
from app.schemas.x.watch_lists import FollowTargetCreateRequest, WatchListEntrySchema, WatchListResponse


class WatchListService:
    def __init__(self, repository: WatchListRepository) -> None:
        self._repository = repository

    def _to_schema(self, entry: WatchListEntry) -> WatchListEntrySchema:
        return WatchListEntrySchema.model_validate(entry.model_dump())

    async def list_follow_targets(self, app_user_id: str) -> WatchListResponse:
        entries = await self._repository.list_entries(app_user_id, WatchListType.FOLLOW_TARGETS)
        return WatchListResponse(
            list_type=WatchListType.FOLLOW_TARGETS.value,
            items=[self._to_schema(e) for e in entries],
        )

    async def add_follow_target(self, app_user_id: str, payload: FollowTargetCreateRequest) -> WatchListEntrySchema:
        entry = WatchListEntry(
            x_user_id=payload.x_user_id,
            username=payload.username,
            name=payload.name,
            added_at=datetime.now(timezone.utc),
        )
        await self._repository.add_entry(app_user_id, WatchListType.FOLLOW_TARGETS, entry)
        return self._to_schema(entry)

    async def remove_follow_target(self, app_user_id: str, x_user_id: str) -> bool:
        removed = await self._repository.remove_entry(app_user_id, WatchListType.FOLLOW_TARGETS, x_user_id)
        return removed > 0

    async def list_following(self, app_user_id: str) -> WatchListResponse:
        entries = await self._repository.list_entries(app_user_id, WatchListType.FOLLOWING)
        return WatchListResponse(list_type=WatchListType.FOLLOWING.value, items=[self._to_schema(e) for e in entries])

    async def list_mutual_followers(self, app_user_id: str) -> WatchListResponse:
        entries = await self._repository.list_entries(app_user_id, WatchListType.MUTUAL_FOLLOWERS)
        return WatchListResponse(
            list_type=WatchListType.MUTUAL_FOLLOWERS.value,
            items=[self._to_schema(e) for e in entries],
        )

    async def replace_following(self, app_user_id: str, entries: list[WatchListEntry]) -> None:
        await self._repository.replace_all(app_user_id, WatchListType.FOLLOWING, entries)

    async def replace_mutual_followers(self, app_user_id: str, entries: list[WatchListEntry]) -> None:
        await self._repository.replace_all(app_user_id, WatchListType.MUTUAL_FOLLOWERS, entries)
