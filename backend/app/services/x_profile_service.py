"""X profile retrieval and caching."""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import Settings
from app.core.exceptions import NotFoundError
from app.integrations.x.client import XAPIClient
from app.infrastructure.x.rate_limit_state import XRateLimitStateStore
from app.models.x.user import XProfile
from app.repositories.x_profile_repository import XProfileRepository
from app.schemas.x.profile import XProfileResponse
from app.services.x_token_service import XTokenService


class XProfileService:
    USER_FIELDS = "id,name,username,description,profile_image_url,public_metrics,created_at"

    def __init__(
        self,
        settings: Settings,
        token_service: XTokenService,
        profile_repository: XProfileRepository,
        rate_limit_store: XRateLimitStateStore,
    ) -> None:
        self._settings = settings
        self._token_service = token_service
        self._profiles = profile_repository
        self._rate_limit_store = rate_limit_store

    def _to_profile(self, data) -> XProfile:
        metrics = data.public_metrics or {}
        return XProfile(
            x_user_id=data.id,
            username=data.username,
            name=data.name,
            description=data.description,
            profile_image_url=data.profile_image_url,
            followers_count=metrics.get("followers_count"),
            following_count=metrics.get("following_count"),
            tweet_count=metrics.get("tweet_count"),
            synced_at=datetime.now(timezone.utc),
        )

    def _to_schema(self, profile: XProfile) -> XProfileResponse:
        return XProfileResponse.model_validate(profile.model_dump())

    async def get_authenticated_profile(self, app_user_id: str) -> XProfileResponse:
        access = await self._token_service.get_access_token(app_user_id)
        async with XAPIClient(self._settings, access_token=access, rate_limit_store=self._rate_limit_store) as client:
            response = await client.get_me(user_fields=self.USER_FIELDS)
        if response.data is None:
            raise NotFoundError("X profile not found")
        profile = self._to_profile(response.data)
        await self._profiles.save_profile(app_user_id, profile)
        return self._to_schema(profile)

    async def lookup_by_username(self, app_user_id: str, username: str) -> XProfileResponse:
        access = await self._token_service.get_access_token(app_user_id)
        async with XAPIClient(self._settings, access_token=access, rate_limit_store=self._rate_limit_store) as client:
            response = await client.get_user_by_username(username, user_fields=self.USER_FIELDS)
        if response.data is None:
            raise NotFoundError(f"X user @{username} not found")
        return self._to_schema(self._to_profile(response.data))

    async def get_cached_profile(self, app_user_id: str) -> XProfileResponse | None:
        cached = await self._profiles.get_profile(app_user_id)
        if cached is None:
            return None
        return self._to_schema(cached)
