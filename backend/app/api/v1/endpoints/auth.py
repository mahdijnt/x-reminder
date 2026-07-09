"""Dashboard authentication endpoints (PRD-compatible /auth routes)."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.core.auth_context import AppUserIdDep
from app.core.dependencies import AuthServiceDep, SettingsDep, XOAuthServiceDep
from app.schemas.responses import APIResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/x/login")
async def x_login(
    oauth_service: XOAuthServiceDep,
    auth_service: AuthServiceDep,
    settings: SettingsDep,
    app_user_id: str | None = Query(default=None),
    redirect: str | None = Query(default=None),
) -> RedirectResponse:
    user_id = app_user_id.strip() if app_user_id and app_user_id.strip() else auth_service.new_app_user_id()
    url, _state = await oauth_service.create_authorization(user_id)
    response = RedirectResponse(url=url, status_code=302)
    response.set_cookie("xr_oauth_user", user_id, httponly=True, secure=settings.is_production, samesite="lax", max_age=600)
    if redirect:
        response.set_cookie("xr_oauth_redirect", redirect, httponly=True, secure=settings.is_production, samesite="lax", max_age=600)
    return response


@router.get("/x/callback")
async def x_callback(
    oauth_service: XOAuthServiceDep,
    auth_service: AuthServiceDep,
    settings: SettingsDep,
    code: str = Query(..., min_length=1),
    state: str = Query(..., min_length=1),
    app_user_id: str | None = Query(default=None),
) -> RedirectResponse:
    app_user_id_resolved, _stored, username = await oauth_service.handle_callback(code, state)
    session = await auth_service.create_x_session(app_user_id_resolved, remember_me=True, x_username=username)
    frontend_base = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"
    redirect_url = f"{frontend_base.rstrip('/')}/login?x_auth=success"
    response = RedirectResponse(url=redirect_url, status_code=302)
    max_age = 60 * 60 * 24 * 30
    response.set_cookie(
        "xr_session",
        "1",
        httponly=False,
        secure=settings.is_production,
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    response.set_cookie(
        "xr_auth_token",
        session["accessToken"],
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    return response


@router.post("/logout")
async def auth_logout(
    auth_service: AuthServiceDep,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> APIResponse[dict]:
    data = await auth_service.logout(authorization)
    return APIResponse.ok(data=data, message="Logged out")


@router.get("/me")
async def auth_me(
    auth_service: AuthServiceDep,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> APIResponse[dict]:
    user = await auth_service.get_me(authorization)
    return APIResponse.ok(data=user)


@router.post("/x/session")
async def x_create_session(
    auth_service: AuthServiceDep,
    app_user_id: str = Query(..., min_length=1),
    username: str | None = Query(default=None),
) -> APIResponse[dict]:
    data = await auth_service.create_x_session(app_user_id, remember_me=True, x_username=username)
    return APIResponse.ok(data=data)
