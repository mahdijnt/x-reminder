"""On-demand and scheduled synchronization from X API."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from app.core.config import Settings
from app.models.x.watch_list import WatchListEntry, WatchListType
from app.repositories.x_profile_repository import XProfileRepository
from app.repositories.x_watch_list_repository import WatchListRepository
from app.schemas.x.watch_lists import WatchListSyncResponse
from app.services.x_profile_service import XProfileService
from app.services.x_relationship_service import XRelationshipService
from app.services.x_token_service import XTokenService

logger = logging.getLogger(__name__)


class XSyncService:
    def __init__(
        self,
        settings: Settings,
        token_service: XTokenService,
        profile_service: XProfileService,
        relationship_service: XRelationshipService,
        profile_repository: XProfileRepository,
        watch_list_repository: WatchListRepository,
    ) -> None:
        self._settings = settings
        self._token_service = token_service
        self._profile_service = profile_service
        self._relationship_service = relationship_service
        self._profiles = profile_repository
        self._watch_lists = watch_list_repository

    async def _resolve_x_user_id(self, app_user_id: str) -> str:
        x_user_id = await self._token_service.get_stored_x_user_id(app_user_id)
        if x_user_id:
            return x_user_id
        profile = await self._profile_service.get_authenticated_profile(app_user_id)
        return profile.x_user_id

    async def _collect_all_following(self, app_user_id: str, x_user_id: str) -> list[WatchListEntry]:
        entries: list[WatchListEntry] = []
        token: str | None = None
        while True:
            page = await self._relationship_service.get_following(app_user_id, x_user_id, pagination_token=token)
            for user in page.items:
                entries.append(
                    WatchListEntry(
                        x_user_id=user.x_user_id,
                        username=user.username,
                        name=user.name,
                        added_at=datetime.now(timezone.utc),
                    )
                )
            token = page.next_token
            if not token:
                break
        return entries

    async def sync_account(self, app_user_id: str) -> WatchListSyncResponse:
        x_user_id = await self._resolve_x_user_id(app_user_id)
        await self._profile_service.get_authenticated_profile(app_user_id)
        following_entries = await self._collect_all_following(app_user_id, x_user_id)
        await self._watch_lists.replace_all(app_user_id, WatchListType.FOLLOWING, following_entries)

        mutual_page = await self._relationship_service.get_mutual_followers(app_user_id, x_user_id)
        mutual_entries = [
            WatchListEntry(
                x_user_id=item.x_user_id,
                username=item.username,
                name=item.name,
                added_at=datetime.now(timezone.utc),
            )
            for item in mutual_page.items
        ]
        await self._watch_lists.replace_all(app_user_id, WatchListType.MUTUAL_FOLLOWERS, mutual_entries)

        now = int(time.time())
        await self._profiles.set_last_scan(app_user_id, now)
        logger.info(
            "x_sync_completed",
            extra={
                "app_user_id": app_user_id,
                "following_count": len(following_entries),
                "mutual_followers_count": len(mutual_entries),
            },
        )
        return WatchListSyncResponse(
            synced=True,
            following_count=len(following_entries),
            mutual_followers_count=len(mutual_entries),
            profile_updated=True,
            last_scan_timestamp=now,
        )
