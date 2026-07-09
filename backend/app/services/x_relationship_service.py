"""Followers, following, and mutual followers."""

from __future__ import annotations

from app.core.config import Settings
from app.integrations.x.client import XAPIClient
from app.infrastructure.x.rate_limit_state import XRateLimitStateStore
from app.schemas.x.relationships import PaginatedUsersResponse, XUserSummary
from app.services.x_token_service import XTokenService


class XRelationshipService:
    def __init__(
        self,
        settings: Settings,
        token_service: XTokenService,
        rate_limit_store: XRateLimitStateStore,
    ) -> None:
        self._settings = settings
        self._token_service = token_service
        self._rate_limit_store = rate_limit_store

    async def _client_for(self, app_user_id: str) -> XAPIClient:
        access = await self._token_service.get_access_token(app_user_id)
        return XAPIClient(self._settings, access_token=access, rate_limit_store=self._rate_limit_store)

    def _map_users(self, response) -> PaginatedUsersResponse:
        users = response.data or []
        items = [XUserSummary(x_user_id=u.id, username=u.username, name=u.name) for u in users]
        next_token = response.meta.next_token if response.meta else None
        return PaginatedUsersResponse(items=items, next_token=next_token)

    async def get_followers(
        self,
        app_user_id: str,
        user_id: str,
        *,
        pagination_token: str | None = None,
    ) -> PaginatedUsersResponse:
        client = await self._client_for(app_user_id)
        async with client:
            response = await client.get_followers(user_id, pagination_token=pagination_token)
        return self._map_users(response)

    async def get_following(
        self,
        app_user_id: str,
        user_id: str,
        *,
        pagination_token: str | None = None,
    ) -> PaginatedUsersResponse:
        client = await self._client_for(app_user_id)
        async with client:
            response = await client.get_following(user_id, pagination_token=pagination_token)
        return self._map_users(response)

    async def get_mutual_followers(self, app_user_id: str, user_id: str) -> PaginatedUsersResponse:
        followers: dict[str, XUserSummary] = {}
        token: str | None = None
        while True:
            page = await self.get_followers(app_user_id, user_id, pagination_token=token)
            for item in page.items:
                followers[item.x_user_id] = item
            token = page.next_token
            if not token:
                break

        following: dict[str, XUserSummary] = {}
        token = None
        while True:
            page = await self.get_following(app_user_id, user_id, pagination_token=token)
            for item in page.items:
                following[item.x_user_id] = item
            token = page.next_token
            if not token:
                break

        mutual_ids = set(followers.keys()) & set(following.keys())
        items = [followers[uid] for uid in sorted(mutual_ids)]
        return PaginatedUsersResponse(items=items, next_token=None)
