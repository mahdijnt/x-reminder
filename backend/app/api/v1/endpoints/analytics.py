from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query

from app.core.auth_context import AppUserIdDep
from app.core.dependencies import AnalyticsServiceDep
from app.schemas.analytics import (
    AccountRankingResponse,
    AnalyticsExportResponse,
    AnalyticsGranularity,
    AnalyticsSeriesResponse,
    AnalyticsSummaryResponse,
    ExportFormat,
    ReportScope,
)
from app.schemas.responses import APIResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _filters(
    service,
    start_date: date | None,
    end_date: date | None,
    list_type: str | None,
    account: str | None,
    granularity: AnalyticsGranularity,
):
    return service.default_filters(start_date, end_date, list_type, account, granularity)


@router.get("/summary", response_model=APIResponse[AnalyticsSummaryResponse])
async def get_summary(
    app_user_id: AppUserIdDep,
    service: AnalyticsServiceDep,
    start_date: date | None = None,
    end_date: date | None = None,
    list_type: str | None = None,
    account: str | None = None,
    granularity: AnalyticsGranularity = AnalyticsGranularity.DAILY,
):
    filters = _filters(service, start_date, end_date, list_type, account, granularity)
    dataset = await service.get_dataset(app_user_id, filters)
    return APIResponse.ok(data=AnalyticsSummaryResponse(filters=filters, kpis=dataset.kpis))


@router.get("/follower-growth", response_model=APIResponse[AnalyticsSeriesResponse])
async def get_follower_growth(
    app_user_id: AppUserIdDep,
    service: AnalyticsServiceDep,
    start_date: date | None = None,
    end_date: date | None = None,
    list_type: str | None = None,
    account: str | None = None,
    granularity: AnalyticsGranularity = AnalyticsGranularity.DAILY,
):
    filters = _filters(service, start_date, end_date, list_type, account, granularity)
    dataset = await service.get_dataset(app_user_id, filters)
    return APIResponse.ok(data=AnalyticsSeriesResponse(filters=filters, series=dataset.follower_growth))


@router.get("/engagement-timeline", response_model=APIResponse[AnalyticsSeriesResponse])
async def get_engagement_timeline(
    app_user_id: AppUserIdDep,
    service: AnalyticsServiceDep,
    start_date: date | None = None,
    end_date: date | None = None,
    list_type: str | None = None,
    account: str | None = None,
    granularity: AnalyticsGranularity = AnalyticsGranularity.DAILY,
):
    filters = _filters(service, start_date, end_date, list_type, account, granularity)
    dataset = await service.get_dataset(app_user_id, filters)
    return APIResponse.ok(data=AnalyticsSeriesResponse(filters=filters, series=dataset.engagement_timeline))


@router.get("/most-active", response_model=APIResponse[AccountRankingResponse])
async def get_most_active_accounts(
    app_user_id: AppUserIdDep,
    service: AnalyticsServiceDep,
    start_date: date | None = None,
    end_date: date | None = None,
    list_type: str | None = None,
    account: str | None = None,
    granularity: AnalyticsGranularity = AnalyticsGranularity.DAILY,
):
    filters = _filters(service, start_date, end_date, list_type, account, granularity)
    dataset = await service.get_dataset(app_user_id, filters)
    return APIResponse.ok(data=AccountRankingResponse(filters=filters, items=dataset.most_active_accounts))


@router.get("/most-valuable", response_model=APIResponse[AccountRankingResponse])
async def get_most_valuable_accounts(
    app_user_id: AppUserIdDep,
    service: AnalyticsServiceDep,
    start_date: date | None = None,
    end_date: date | None = None,
    list_type: str | None = None,
    account: str | None = None,
    granularity: AnalyticsGranularity = AnalyticsGranularity.DAILY,
):
    filters = _filters(service, start_date, end_date, list_type, account, granularity)
    dataset = await service.get_dataset(app_user_id, filters)
    return APIResponse.ok(data=AccountRankingResponse(filters=filters, items=dataset.most_valuable_accounts))


@router.get("/reports/{scope}")
async def get_period_report(
    scope: ReportScope,
    app_user_id: AppUserIdDep,
    service: AnalyticsServiceDep,
    start_date: date | None = None,
    end_date: date | None = None,
    list_type: str | None = None,
    account: str | None = None,
):
    filters = _filters(service, start_date, end_date, list_type, account, AnalyticsGranularity(scope.value))
    report = await service.build_report(app_user_id, scope, filters)
    return APIResponse.ok(data=report)


@router.get("/export", response_model=APIResponse[AnalyticsExportResponse])
async def export_analytics(
    app_user_id: AppUserIdDep,
    service: AnalyticsServiceDep,
    report_type: str = Query(default="summary", min_length=2),
    format: ExportFormat = ExportFormat.JSON,
    start_date: date | None = None,
    end_date: date | None = None,
    list_type: str | None = None,
    account: str | None = None,
    granularity: AnalyticsGranularity = AnalyticsGranularity.DAILY,
):
    filters = _filters(service, start_date, end_date, list_type, account, granularity)
    exported = await service.export_report(app_user_id, report_type, format, filters)
    return APIResponse.ok(data=exported)
