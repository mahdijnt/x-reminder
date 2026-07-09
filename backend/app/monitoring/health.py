from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import Settings
from app.monitoring.monitoring_engine import MonitoringEngine
from app.monitoring.models import PollListType


async def monitoring_health(settings: Settings, engine: MonitoringEngine | None) -> dict:
    if not settings.MONITORING_ENABLED:
        return {"status": "disabled", "detail": "MONITORING_ENABLED=false"}
    if engine is None:
        return {"status": "unavailable", "detail": "Monitoring engine not initialized"}
    status = await engine.status()
    last_polls = {}
    for list_type in PollListType:
        for user_id in settings.MONITORING_APP_USER_IDS:
            ts = await engine.last_poll_store.get(user_id, list_type.value)
            last_polls[f"{user_id}:{list_type.value}"] = ts.isoformat() if ts else None
    overall = "ok" if status.get("scheduler_running") and status.get("worker_running") else "degraded"
    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engine": status,
        "last_successful_poll": last_polls,
    }
