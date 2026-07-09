from __future__ import annotations

from fastapi import APIRouter, Request

from app.core.auth_context import AppUserIdDep
from app.core.dependencies import SettingsDep
from app.notifications.models import NotificationJobPayload, NotificationPriority, TweetNotificationData
from app.schemas.notifications import (
    NotificationHistoryData,
    NotificationReportsData,
    NotificationStatusData,
    NotificationTestRequest,
    NotificationTriggerRequest,
)
from app.schemas.responses import APIResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _engine(request: Request):
    return getattr(request.app.state, "notification_engine", None)


@router.get("/status", response_model=APIResponse[NotificationStatusData])
async def notifications_status(request: Request, settings: SettingsDep) -> APIResponse[NotificationStatusData]:
    engine = _engine(request)
    if not settings.NOTIFICATIONS_ENABLED or engine is None:
        data = NotificationStatusData(
            enabled=False,
            worker_enabled=False,
            worker_running=False,
            worker_in_flight=0,
            queue_depth={"total": 0, "high": 0, "normal": 0, "low": 0},
            retry_queue_depth=0,
            failure_queue_depth=0,
            metrics={},
            telegram_configured=bool(settings.TELEGRAM_BOT_TOKEN.strip()),
        )
        return APIResponse.ok(data=data, message="Notifications disabled")
    raw = await engine.status()
    return APIResponse.ok(data=NotificationStatusData(**raw))


@router.get("/history", response_model=APIResponse[NotificationHistoryData])
async def notifications_history(
    request: Request,
    settings: SettingsDep,
    limit: int = 50,
) -> APIResponse[NotificationHistoryData]:
    engine = _engine(request)
    if not settings.NOTIFICATIONS_ENABLED or engine is None:
        return APIResponse.ok(data=NotificationHistoryData(items=[]), message="Notifications disabled")
    items = await engine.history.list_recent(limit=limit)
    return APIResponse.ok(data=NotificationHistoryData(items=items))


@router.get("/reports", response_model=APIResponse[NotificationReportsData])
async def notifications_reports(request: Request, settings: SettingsDep) -> APIResponse[NotificationReportsData]:
    engine = _engine(request)
    if not settings.NOTIFICATIONS_ENABLED or engine is None:
        return APIResponse.ok(
            data=NotificationReportsData(delivery_summary={}, metrics={}, queue_depth={"total": 0}),
            message="Notifications disabled",
        )
    status = await engine.status()
    summary = await engine.history.summary()
    data = NotificationReportsData(
        delivery_summary=summary,
        metrics=status.get("metrics", {}),
        queue_depth=status.get("queue_depth", {}),
    )
    return APIResponse.ok(data=data)


@router.post("/trigger", response_model=APIResponse[dict])
async def notifications_trigger(
    request: Request,
    settings: SettingsDep,
    body: NotificationTriggerRequest,
    app_user_id: AppUserIdDep,
) -> APIResponse[dict]:
    engine = _engine(request)
    if not settings.NOTIFICATIONS_ENABLED or engine is None:
        return APIResponse.fail(message="Notifications disabled", code="notifications_disabled")
    target = body.app_user_id or app_user_id
    result = await engine.jobs.process_pending(target, limit=body.limit)
    return APIResponse.ok(data=result, message="Pending notifications processed")


@router.post("/test", response_model=APIResponse[dict])
async def notifications_test(
    request: Request,
    settings: SettingsDep,
    body: NotificationTestRequest,
    app_user_id: AppUserIdDep,
) -> APIResponse[dict]:
    engine = _engine(request)
    if not settings.NOTIFICATIONS_ENABLED or engine is None:
        return APIResponse.fail(message="Notifications disabled", code="notifications_disabled")
    if not settings.TELEGRAM_BOT_TOKEN.strip():
        return APIResponse.fail(message="TELEGRAM_BOT_TOKEN not configured", code="telegram_not_configured")
    now = datetime.now(timezone.utc)
    tweet = TweetNotificationData(
        tweet_id="test",
        author_id="test",
        username="testuser",
        url="https://x.com/test/status/1",
        created_at=now,
        list_type="following",
    )
    text = body.message or "Test notification from x-reminder"
    payload = NotificationJobPayload(
        app_user_id=app_user_id,
        telegram_id=body.telegram_id,
        priority=NotificationPriority.HIGH,
        tweets=[tweet],
        metadata={"test_message": text},
    )
    from app.notifications.message_builder import build_single_tweet_message
    from app.integrations.telegram.client import TelegramClient

    client = TelegramClient(settings)
    try:
        if body.message:
            await client.send_message(body.telegram_id, body.message)
        else:
            await client.send_message(body.telegram_id, build_single_tweet_message(tweet))
    finally:
        await client.close()
    return APIResponse.ok(data={"telegram_id": body.telegram_id, "job_id": payload.job_id}, message="Test sent")
