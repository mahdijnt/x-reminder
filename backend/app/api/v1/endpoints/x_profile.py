"""X profile and relationship endpoints."""

from fastapi import APIRouter, Query

from app.core.auth_context import AppUserIdDep
from app.core.dependencies import XProfileServiceDep, XRelationshipServiceDep, XTweetServiceDep
from app.schemas.responses import APIResponse
from app.schemas.x.profile import XProfileResponse
from app.schemas.x.relationships import PaginatedUsersResponse
from app.schemas.x.tweets import TweetListResponse

router = APIRouter(prefix="/x", tags=["x"])


@router.get("/profile", response_model=APIResponse[XProfileResponse])
async def get_x_profile(app_user_id: AppUserIdDep, profile_service: XProfileServiceDep) -> APIResponse[XProfileResponse]:
    data = await profile_service.get_authenticated_profile(app_user_id)
    return APIResponse.ok(data=data)


@router.get("/users/{username}", response_model=APIResponse[XProfileResponse])
async def get_x_user_by_username(
    username: str,
    app_user_id: AppUserIdDep,
    profile_service: XProfileServiceDep,
) -> APIResponse[XProfileResponse]:
    data = await profile_service.lookup_by_username(app_user_id, username)
    return APIResponse.ok(data=data)


@router.get("/users/{user_id}/followers", response_model=APIResponse[PaginatedUsersResponse])
async def get_followers(
    user_id: str,
    app_user_id: AppUserIdDep,
    relationship_service: XRelationshipServiceDep,
    pagination_token: str | None = Query(default=None),
) -> APIResponse[PaginatedUsersResponse]:
    data = await relationship_service.get_followers(app_user_id, user_id, pagination_token=pagination_token)
    return APIResponse.ok(data=data)


@router.get("/users/{user_id}/following", response_model=APIResponse[PaginatedUsersResponse])
async def get_following(
    user_id: str,
    app_user_id: AppUserIdDep,
    relationship_service: XRelationshipServiceDep,
    pagination_token: str | None = Query(default=None),
) -> APIResponse[PaginatedUsersResponse]:
    data = await relationship_service.get_following(app_user_id, user_id, pagination_token=pagination_token)
    return APIResponse.ok(data=data)


@router.get("/users/{user_id}/mutual-followers", response_model=APIResponse[PaginatedUsersResponse])
async def get_mutual_followers(
    user_id: str,
    app_user_id: AppUserIdDep,
    relationship_service: XRelationshipServiceDep,
) -> APIResponse[PaginatedUsersResponse]:
    data = await relationship_service.get_mutual_followers(app_user_id, user_id)
    return APIResponse.ok(data=data)


@router.get("/users/{user_id}/tweets", response_model=APIResponse[TweetListResponse])
async def get_user_tweets(
    user_id: str,
    app_user_id: AppUserIdDep,
    tweet_service: XTweetServiceDep,
    since_id: str | None = Query(default=None),
    pagination_token: str | None = Query(default=None),
    include_replies: bool = Query(default=False),
    include_retweets: bool = Query(default=False),
    include_quotes: bool = Query(default=False),
    original_only: bool = Query(default=True),
) -> APIResponse[TweetListResponse]:
    data = await tweet_service.fetch_user_tweets(
        app_user_id,
        user_id,
        since_id=since_id,
        pagination_token=pagination_token,
        include_replies=include_replies,
        include_retweets=include_retweets,
        include_quotes=include_quotes,
        original_only=original_only,
        record_processed=True,
    )
    return APIResponse.ok(data=data)
