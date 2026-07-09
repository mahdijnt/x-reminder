from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class AnalyticsGranularity(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReportScope(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"


class AnalyticsFilters(BaseModel):
    start_date: date
    end_date: date
    list_type: str | None = None
    account: str | None = None
    granularity: AnalyticsGranularity = AnalyticsGranularity.DAILY


class KPIBundle(BaseModel):
    follow_back_rate: float = Field(ge=0, le=1)
    average_follow_back_time_hours: float = Field(ge=0)
    success_rate: float = Field(ge=0, le=1)


class AnalyticsSeriesPoint(BaseModel):
    label: str
    value: float


class ActiveAccountMetric(BaseModel):
    account_id: str
    account: str
    list_type: str
    follows: int
    follow_backs: int
    engagements: int


class ValuableAccountMetric(BaseModel):
    account_id: str
    account: str
    list_type: str
    value_score: float
    avg_follow_back_time_hours: float
    engagement_score: float


class AnalyticsSummaryResponse(BaseModel):
    filters: AnalyticsFilters
    kpis: KPIBundle


class AnalyticsSeriesResponse(BaseModel):
    filters: AnalyticsFilters
    series: list[AnalyticsSeriesPoint]


class AccountRankingResponse(BaseModel):
    filters: AnalyticsFilters
    items: list[ActiveAccountMetric] | list[ValuableAccountMetric]


class PeriodReport(BaseModel):
    scope: ReportScope
    period_label: str
    filters: AnalyticsFilters
    kpis: KPIBundle
    follower_growth: list[AnalyticsSeriesPoint]
    engagement_timeline: list[AnalyticsSeriesPoint]
    most_active_accounts: list[ActiveAccountMetric]
    most_valuable_accounts: list[ValuableAccountMetric]


class AnalyticsExportResponse(BaseModel):
    format: ExportFormat
    filename: str
    content_type: str
    content: str
