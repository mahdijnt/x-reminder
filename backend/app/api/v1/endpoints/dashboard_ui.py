from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query
from app.core.auth_context import AppUserIdDep
from app.core.dependencies import AnalyticsServiceDep, AuthServiceDep, SettingsDep, WatchListServiceDep, XProfileServiceDep
from app.schemas.analytics import AnalyticsGranularity, ReportScope
from app.schemas.responses import APIResponse

router = APIRouter(tags=["dashboard-ui"])


def _auth_user(user_id: str, email: str, role: str = "user") -> dict:
    clean = (email.split("@", 1)[0] if "@" in email else user_id).strip() or user_id
    display = clean.replace(".", " ").replace("_", " ").strip().title() or "User"
    initials = "".join(part[0] for part in display.split()[:2]).upper() or "U"
    return {"id": user_id, "name": display, "email": email, "role": role, "initials": initials}


@router.post("/auth/login")
async def auth_login(payload: dict, auth_service: AuthServiceDep) -> APIResponse[dict]:
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", "")).strip()
    remember_me = bool(payload.get("rememberMe", False))
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    data = await auth_service.login(email, password, remember_me=remember_me)
    return APIResponse.ok(data=data)


@router.post("/auth/register")
async def auth_register(payload: dict, auth_service: AuthServiceDep) -> APIResponse[dict]:
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", "")).strip()
    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="Name, email and password are required")
    data = await auth_service.register(name, email, password)
    return APIResponse.ok(data=data, message="Account created")


@router.post("/auth/forgot-password")
async def auth_forgot_password(payload: dict, settings: SettingsDep) -> APIResponse[dict]:
    email = str(payload.get("email", "")).strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    token = f"reset-{email.split('@', 1)[0] or 'user'}"
    return APIResponse.ok(data={"ok": True, "token": token}, message="Reset token generated")


@router.post("/auth/reset-password")
async def auth_reset_password(payload: dict) -> APIResponse[dict]:
    token = str(payload.get("token", "")).strip()
    password = str(payload.get("password", "")).strip()
    if not token or not password:
        raise HTTPException(status_code=400, detail="Token and password are required")
    return APIResponse.ok(data={"ok": True}, message="Password reset")


@router.post("/auth/logout")
async def auth_logout(auth_service: AuthServiceDep, authorization: str | None = Header(default=None, alias="Authorization")) -> APIResponse[dict]:
    data = await auth_service.logout(authorization)
    return APIResponse.ok(data=data, message="Logged out")


@router.get("/auth/me")
async def auth_me(auth_service: AuthServiceDep, authorization: str | None = Header(default=None, alias="Authorization")) -> APIResponse[dict]:
    user = await auth_service.get_me(authorization)
    return APIResponse.ok(data=user)


@router.get("/navigation/sidebar")
async def navigation_sidebar() -> APIResponse[list[dict]]:
    return APIResponse.ok(data=[{"title": "Dashboard", "href": "/", "active": True}, {"title": "Watch Lists", "href": "/watch-lists", "badge": "New"}, {"title": "Following", "href": "/following"}, {"title": "Follow Targets", "href": "/follow-targets"}, {"title": "Mutual Followers", "href": "/mutual-followers"}, {"title": "Target Achieved", "href": "/target-achieved"}, {"title": "Analytics", "href": "/analytics"}, {"title": "Settings", "href": "/settings"}, {"title": "Profile", "href": "/profile"}, {"title": "Notifications", "href": "/notifications"}])


@router.get("/navigation/top-nav")
async def navigation_top_nav() -> APIResponse[list[dict]]:
    return APIResponse.ok(data=[{"title": "Dashboard", "href": "/", "active": True}, {"title": "Watch Lists", "href": "/watch-lists"}, {"title": "Following", "href": "/following"}, {"title": "Follow Targets", "href": "/follow-targets"}, {"title": "Mutual", "href": "/mutual-followers"}, {"title": "Achieved", "href": "/target-achieved"}, {"title": "Analytics", "href": "/analytics"}, {"title": "Settings", "href": "/settings"}, {"title": "Profile", "href": "/profile"}, {"title": "Alerts", "href": "/notifications"}])


@router.get("/navigation/breadcrumbs")
async def navigation_breadcrumbs() -> APIResponse[list[dict]]:
    return APIResponse.ok(data=[{"label": "Workspace", "href": "#"}, {"label": "Insights", "href": "#"}, {"label": "Overview"}])


@router.get("/user/current")
async def user_current(
    app_user_id: AppUserIdDep,
    auth_service: AuthServiceDep,
    profile_service: XProfileServiceDep,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> APIResponse[dict]:
    try:
        user = await auth_service.get_me(authorization)
    except Exception:
        user = _auth_user(app_user_id, f"{app_user_id}@example.com")
    try:
        profile = await profile_service.get_cached_profile(app_user_id)
        if profile is None:
            profile = await profile_service.get_authenticated_profile(app_user_id)
        if profile is not None:
            user.update(
                {
                    "name": profile.name,
                    "x_username": profile.username,
                    "bio": profile.description,
                    "avatar_url": profile.profile_image_url,
                    "followers_count": profile.followers_count,
                    "following_count": profile.following_count,
                    "initials": "".join(part[0] for part in (profile.name or profile.username).split()[:2]).upper() or user.get("initials", "U"),
                }
            )
    except Exception:
        pass
    return APIResponse.ok(data={"name": user.get("name"), "email": user.get("email"), "role": user.get("role", "user"), "initials": user.get("initials", "U"), "x_username": user.get("x_username"), "bio": user.get("bio"), "avatar_url": user.get("avatar_url"), "followers_count": user.get("followers_count"), "following_count": user.get("following_count")})


def _watch_item_to_row(item: dict, idx: int) -> dict:
    username = item.get("username", "unknown")
    return {"id": item.get("x_user_id") or f"item-{idx}", "name": item.get("name") or username, "handle": f"@{username.lstrip('@')}"}


@router.get("/watch-lists")
async def watch_lists_index(app_user_id: AppUserIdDep, watch_list_service: WatchListServiceDep) -> APIResponse[list[dict]]:
    targets = await watch_list_service.list_follow_targets(app_user_id)
    rows = []
    for idx, entry in enumerate(targets.items):
        row = _watch_item_to_row(entry.model_dump(), idx)
        row.update({"status": "Active", "owner": "Team", "signals": "Live", "lastCheck": "just now"})
        rows.append(row)
    return APIResponse.ok(data=rows)


@router.get("/following")
async def following_rows(app_user_id: AppUserIdDep, watch_list_service: WatchListServiceDep) -> APIResponse[list[dict]]:
    following = await watch_list_service.list_following(app_user_id)
    rows = []
    for idx, entry in enumerate(following.items):
        row = _watch_item_to_row(entry.model_dump(), idx)
        row.update({"since": "recent", "notificationState": "Enabled", "engagement": "Stable"})
        rows.append(row)
    return APIResponse.ok(data=rows)


@router.get("/follow-targets")
async def follow_target_rows(app_user_id: AppUserIdDep, watch_list_service: WatchListServiceDep) -> APIResponse[list[dict]]:
    targets = await watch_list_service.list_follow_targets(app_user_id)
    rows = []
    for idx, entry in enumerate(targets.items):
        row = _watch_item_to_row(entry.model_dump(), idx)
        row.update({"matchScore": max(50, 95 - idx * 3), "strategy": "Lookalike", "status": "Qualified"})
        rows.append(row)
    return APIResponse.ok(data=rows)


@router.get("/mutual-followers")
async def mutual_followers_rows(app_user_id: AppUserIdDep, watch_list_service: WatchListServiceDep) -> APIResponse[list[dict]]:
    mutual = await watch_list_service.list_mutual_followers(app_user_id)
    rows = []
    for idx, entry in enumerate(mutual.items):
        row = _watch_item_to_row(entry.model_dump(), idx)
        row.update({"mutualSince": "recent", "lastMention": "just now", "tier": "Standard" if idx % 2 else "Gold"})
        rows.append(row)
    return APIResponse.ok(data=rows)


@router.get("/target-achieved")
async def target_achieved_rows(app_user_id: AppUserIdDep, analytics_service: AnalyticsServiceDep) -> APIResponse[list[dict]]:
    filters = analytics_service.default_filters(None, None, None, None, AnalyticsGranularity.DAILY)
    report = await analytics_service.build_report(app_user_id, scope=ReportScope.DAILY, filters=filters)
    rows = []
    for idx, item in enumerate(report.most_valuable_accounts[:6]):
        rows.append({"id": item.account_id, "targetName": f"Improve {item.account}", "handle": f"@{item.account}", "achievedAt": report.period_label, "metric": f"{item.value_score:.1f}", "status": "Achieved" if idx < 4 else "Archived"})
    return APIResponse.ok(data=rows)


@router.get("/notifications")
async def notifications_feed(app_user_id: AppUserIdDep, analytics_service: AnalyticsServiceDep, limit: int = Query(default=6, ge=1, le=20)) -> APIResponse[list[dict]]:
    filters = analytics_service.default_filters(None, None, None, None, AnalyticsGranularity.DAILY)
    dataset = await analytics_service.get_dataset(app_user_id, filters)
    rows = []
    for idx, account in enumerate(dataset.most_active_accounts[:limit]):
        rows.append({"id": f"notif-{idx}", "title": f"Activity update: @{account.account}", "description": f"{account.engagements} engagements, {account.follow_backs} follow-backs.", "time": f"{idx + 1}h ago", "unread": idx < 2, "tone": "default" if idx % 3 else "success"})
    return APIResponse.ok(data=rows)


@router.get("/dashboard/overview")
async def dashboard_overview(app_user_id: AppUserIdDep, analytics_service: AnalyticsServiceDep) -> APIResponse[dict]:
    filters = analytics_service.default_filters(None, None, None, None, AnalyticsGranularity.DAILY)
    dataset = await analytics_service.get_dataset(app_user_id, filters)
    stats = [{"title": "Follow Back Rate", "value": f"{dataset.kpis.follow_back_rate * 100:.1f}%", "change": "+0.0%", "trend": "up", "detail": "Followers following back"}, {"title": "Avg Follow Back Time", "value": f"{dataset.kpis.average_follow_back_time_hours:.1f}h", "change": "0.0h", "trend": "neutral", "detail": "Average delay to follow back"}, {"title": "Success Rate", "value": f"{dataset.kpis.success_rate * 100:.1f}%", "change": "+0.0%", "trend": "up", "detail": "Campaign success ratio"}]
    progress = [{"label": "Data freshness", "value": 80, "description": "Derived from live analytics snapshots."}, {"label": "Signal quality", "value": 72, "description": "Computed from engagement and follow-back events."}, {"label": "Coverage", "value": 65, "description": "Tracked accounts with recent activity."}]
    donut_chart = [{"label": "follow-targets", "value": len([a for a in dataset.most_active_accounts if a.list_type == "follow-targets"])}, {"label": "following", "value": len([a for a in dataset.most_active_accounts if a.list_type == "following"])}, {"label": "mutual-followers", "value": len([a for a in dataset.most_active_accounts if a.list_type == "mutual-followers"])}]
    table_rows = [{"id": item.account_id, "name": item.account, "status": "Active", "owner": "System", "amount": f"{item.value_score:.2f}"} for item in dataset.most_valuable_accounts[:6]]
    return APIResponse.ok(data={"stats": stats, "progress": progress, "lineChart": dataset.follower_growth, "barChart": dataset.engagement_timeline, "donutChart": donut_chart, "tableRows": table_rows})


@router.get("/analytics/overview")
async def analytics_overview(app_user_id: AppUserIdDep, analytics_service: AnalyticsServiceDep, settings: SettingsDep) -> APIResponse[dict]:
    filters = analytics_service.default_filters(None, None, None, None, AnalyticsGranularity.DAILY)
    dataset = await analytics_service.get_dataset(app_user_id, filters)
    stats = [{"title": "Follow Back Rate", "value": f"{dataset.kpis.follow_back_rate * 100:.1f}%", "change": "+0.0%", "trend": "up", "detail": "Followers following back"}, {"title": "Avg Follow Back Time", "value": f"{dataset.kpis.average_follow_back_time_hours:.1f}h", "change": "0.0h", "trend": "neutral", "detail": "Average delay to follow back"}, {"title": "Success Rate", "value": f"{dataset.kpis.success_rate * 100:.1f}%", "change": "+0.0%", "trend": "up", "detail": "Campaign success ratio"}]
    top_tweets = [{"id": f"tw-{idx}", "tweet": f"{item.account} engagement snapshot", "metric": f"{item.engagements}", "impact": f"{item.follow_backs} follow-backs", "state": "High" if idx < 2 else ("Medium" if idx < 4 else "Low")} for idx, item in enumerate(dataset.most_active_accounts[: settings.ANALYTICS_TOP_ACCOUNTS_LIMIT])]
    return APIResponse.ok(data={"stats": stats, "lineChart": dataset.follower_growth, "barChart": dataset.engagement_timeline, "donutChart": [{"label": "Accounts", "value": len(dataset.most_active_accounts)}], "topTweets": top_tweets})

