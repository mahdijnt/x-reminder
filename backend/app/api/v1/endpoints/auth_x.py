"""X OAuth 2.0 endpoints."""

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from app.core.auth_context import AppUserIdDep
from app.core.dependencies import XOAuthServiceDep
from app.schemas.responses import APIResponse
from app.schemas.x.oauth import XOAuthAuthorizeData, XOAuthCallbackData, XOAuthDisconnectData

router = APIRouter(prefix="/x/oauth", tags=["x-oauth"])


@router.get("/authorize", response_model=APIResponse[XOAuthAuthorizeData])
async def x_oauth_authorize(
    oauth_service: XOAuthServiceDep,
    app_user_id: str = Query(..., min_length=1, description="Internal app user id"),
) -> APIResponse[XOAuthAuthorizeData]:
    url, state = await oauth_service.create_authorization(app_user_id)
    return APIResponse.ok(data=XOAuthAuthorizeData(authorization_url=url, state=state))


@router.get("/authorize/redirect")
async def x_oauth_authorize_redirect(
    oauth_service: XOAuthServiceDep,
    app_user_id: str = Query(..., min_length=1),
) -> RedirectResponse:
    url, _state = await oauth_service.create_authorization(app_user_id)
    return RedirectResponse(url=url, status_code=302)


@router.get("/callback", response_model=APIResponse[XOAuthCallbackData])
async def x_oauth_callback(
    oauth_service: XOAuthServiceDep,
    code: str = Query(..., min_length=1),
    state: str = Query(..., min_length=1),
) -> APIResponse[XOAuthCallbackData]:
    stored, username = await oauth_service.handle_callback(code, state)
    return APIResponse.ok(
        data=XOAuthCallbackData(connected=True, x_user_id=stored.x_user_id, username=username),
        message="X account connected",
    )


@router.post("/disconnect", response_model=APIResponse[XOAuthDisconnectData])
async def x_oauth_disconnect(
    app_user_id: AppUserIdDep,
    oauth_service: XOAuthServiceDep,
) -> APIResponse[XOAuthDisconnectData]:
    await oauth_service.disconnect(app_user_id)
    return APIResponse.ok(data=XOAuthDisconnectData(disconnected=True), message="X account disconnected")
