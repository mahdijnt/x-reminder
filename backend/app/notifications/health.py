from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import Settings


async def notifications_health(settings: Settings, engine) -> dict:
    if not settings.NOTIFICATIONS_ENABLED or engine is None:
        return {
            "status": "disabled",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engine": {"enabled": False},
        }
    status = await engine.status()
    ok = status.get("worker_running") or not settings.NOTIFICATIONS_WORKER_ENABLED
    overall = "ok" if ok else "degraded"
    if not status.get("telegram_configured"):
        overall = "degraded"
    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engine": status,
    }
