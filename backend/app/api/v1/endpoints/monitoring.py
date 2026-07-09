from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from app.core.auth_context import AppUserIdDep
from app.core.dependencies import SettingsDep
from app.monitoring.models import JobType
from app.schemas.monitoring import (
    JobHistoryListData,
    MonitoringHealthData,
    MonitoringStatusData,
    TriggerJobData,
)
from app.schemas.responses import APIResponse

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def _engine(request: Request):
    return getattr(request.app.state, "monitoring_engine", None)


@router.get("/status", response_model=APIResponse[MonitoringStatusData])
async def monitoring_status(request: Request, settings: SettingsDep) -> APIResponse[MonitoringStatusData]:
    engine = _engine(request)
    if not settings.MONITORING_ENABLED or engine is None:
        data = MonitoringStatusData(
            enabled=False,
            scheduler_running=False,
            worker_running=False,
            worker_in_flight=0,
            queue_depth=0,
            retry_queue_depth=0,
            metrics={},
        )
        return APIResponse.ok(data=data, message="Monitoring disabled")
    raw = await engine.status()
    return APIResponse.ok(data=MonitoringStatusData(**raw))


@router.get("/health", response_model=APIResponse[dict])
async def monitoring_health_endpoint(request: Request, settings: SettingsDep) -> APIResponse[dict]:
    from app.monitoring.health import monitoring_health

    engine = _engine(request)
    data = await monitoring_health(settings, engine)
    return APIResponse.ok(data=data)


@router.get("/jobs", response_model=APIResponse[JobHistoryListData])
async def monitoring_jobs(request: Request, settings: SettingsDep, limit: int = 50) -> APIResponse[JobHistoryListData]:
    engine = _engine(request)
    if not settings.MONITORING_ENABLED or engine is None:
        return APIResponse.ok(data=JobHistoryListData(items=[]), message="Monitoring disabled")
    items = await engine.history.list_recent(limit=limit)
    return APIResponse.ok(data=JobHistoryListData(items=items))


@router.get("/metrics")
async def monitoring_metrics(request: Request, settings: SettingsDep, format: str = "json"):
    engine = _engine(request)
    if not settings.MONITORING_ENABLED or engine is None:
        if format == "prometheus":
            return PlainTextResponse("")
        return APIResponse.ok(data={})
    data = await engine.metrics.snapshot()
    if format == "prometheus":
        return PlainTextResponse(engine.metrics.prometheus_text(data), media_type="text/plain")
    return APIResponse.ok(data=data)


@router.post("/trigger/{job_type}", response_model=APIResponse[TriggerJobData])
async def trigger_job(
    job_type: JobType,
    request: Request,
    settings: SettingsDep,
    app_user_id: AppUserIdDep,
) -> APIResponse[TriggerJobData]:
    engine = _engine(request)
    if not settings.MONITORING_ENABLED or engine is None:
        return APIResponse.fail(message="Monitoring disabled", code="monitoring_disabled")
    payload = await engine.task_manager.enqueue_job(job_type, app_user_id, priority=2)
    data = TriggerJobData(job_id=payload.job_id, job_type=payload.job_type, app_user_id=payload.app_user_id)
    return APIResponse.ok(data=data, message="Job enqueued")
