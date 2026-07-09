"""Watch list endpoints."""

from fastapi import APIRouter, Query, status

from app.core.auth_context import AppUserIdDep
from app.core.dependencies import WatchListServiceDep, XSyncServiceDep
from app.schemas.responses import APIResponse
from app.schemas.x.watch_lists import FollowTargetCreateRequest, WatchListResponse, WatchListSyncResponse

router = APIRouter(prefix="/watch-lists", tags=["watch-lists"])


@router.get("/follow-targets", response_model=APIResponse[WatchListResponse])
async def list_follow_targets(app_user_id: AppUserIdDep, watch_list_service: WatchListServiceDep) -> APIResponse[WatchListResponse]:
    return APIResponse.ok(data=await watch_list_service.list_follow_targets(app_user_id))


@router.post("/follow-targets", response_model=APIResponse[WatchListResponse], status_code=status.HTTP_201_CREATED)
async def add_follow_target(
    payload: FollowTargetCreateRequest,
    app_user_id: AppUserIdDep,
    watch_list_service: WatchListServiceDep,
) -> APIResponse[WatchListResponse]:
    await watch_list_service.add_follow_target(app_user_id, payload)
    return APIResponse.ok(data=await watch_list_service.list_follow_targets(app_user_id), message="Follow target added")


@router.delete("/follow-targets", response_model=APIResponse[WatchListResponse])
async def delete_follow_target(
    app_user_id: AppUserIdDep,
    watch_list_service: WatchListServiceDep,
    x_user_id: str = Query(..., min_length=1),
) -> APIResponse[WatchListResponse]:
    await watch_list_service.remove_follow_target(app_user_id, x_user_id)
    return APIResponse.ok(data=await watch_list_service.list_follow_targets(app_user_id), message="Follow target removed")


@router.get("/following", response_model=APIResponse[WatchListResponse])
async def list_following(app_user_id: AppUserIdDep, watch_list_service: WatchListServiceDep) -> APIResponse[WatchListResponse]:
    return APIResponse.ok(data=await watch_list_service.list_following(app_user_id))


@router.get("/mutual-followers", response_model=APIResponse[WatchListResponse])
async def list_mutual_followers(app_user_id: AppUserIdDep, watch_list_service: WatchListServiceDep) -> APIResponse[WatchListResponse]:
    return APIResponse.ok(data=await watch_list_service.list_mutual_followers(app_user_id))


@router.post("/sync", response_model=APIResponse[WatchListSyncResponse])
async def sync_watch_lists(app_user_id: AppUserIdDep, sync_service: XSyncServiceDep) -> APIResponse[WatchListSyncResponse]:
    data = await sync_service.sync_account(app_user_id)
    return APIResponse.ok(data=data, message="Watch lists synchronized from X")
