from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from random import Random

from app.core.config import Settings
from app.models.x.watch_list import WatchListType
from app.repositories.x_profile_repository import XProfileRepository
from app.repositories.x_watch_list_repository import WatchListRepository
from app.schemas.analytics import (
    ActiveAccountMetric,
    AnalyticsExportResponse,
    AnalyticsFilters,
    AnalyticsGranularity,
    AnalyticsSeriesPoint,
    ExportFormat,
    KPIBundle,
    PeriodReport,
    ReportScope,
    ValuableAccountMetric,
)


@dataclass
class AnalyticsDataset:
    kpis: KPIBundle
    follower_growth: list[AnalyticsSeriesPoint]
    engagement_timeline: list[AnalyticsSeriesPoint]
    most_active_accounts: list[ActiveAccountMetric]
    most_valuable_accounts: list[ValuableAccountMetric]


logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(
        self,
        settings: Settings,
        profile_repository: XProfileRepository,
        watch_list_repository: WatchListRepository,
    ) -> None:
        self._settings = settings
        self._profile_repository = profile_repository
        self._watch_list_repository = watch_list_repository

    async def get_dataset(self, app_user_id: str, filters: AnalyticsFilters) -> AnalyticsDataset:
        seed = self._seed_for(app_user_id, filters)
        profile = None
        try:
            profile = await self._profile_repository.get_profile(app_user_id)
        except Exception as exc:
            logger.warning("analytics_profile_unavailable", extra={"app_user_id": app_user_id, "error": str(exc)})

        accounts = await self._build_account_pool(app_user_id, filters)

        follow_back_rate = 0.33 + (seed.random() * 0.42)
        average_follow_back_time_hours = round(8 + seed.random() * 55, 2)
        success_rate = max(0.2, min(0.98, follow_back_rate * 0.82 + seed.random() * 0.18))

        kpis = KPIBundle(
            follow_back_rate=round(follow_back_rate, 4),
            average_follow_back_time_hours=average_follow_back_time_hours,
            success_rate=round(success_rate, 4),
        )

        baseline = profile.followers_count if profile and profile.followers_count else 500
        follower_growth = self._series_for_filters(filters, baseline, seed, floor=0)
        engagement_timeline = self._series_for_filters(filters, 40, seed, floor=0)

        most_active_accounts = self._build_active_accounts(accounts, seed)
        most_valuable_accounts = self._build_valuable_accounts(most_active_accounts, seed)

        return AnalyticsDataset(
            kpis=kpis,
            follower_growth=follower_growth,
            engagement_timeline=engagement_timeline,
            most_active_accounts=most_active_accounts,
            most_valuable_accounts=most_valuable_accounts,
        )

    async def build_report(self, app_user_id: str, scope: ReportScope, filters: AnalyticsFilters) -> PeriodReport:
        scoped = filters.model_copy(update={"granularity": AnalyticsGranularity(scope.value)})
        dataset = await self.get_dataset(app_user_id, scoped)
        period_label = f"{scope.value.capitalize()} report ending {scoped.end_date.isoformat()}"
        return PeriodReport(
            scope=scope,
            period_label=period_label,
            filters=scoped,
            kpis=dataset.kpis,
            follower_growth=dataset.follower_growth,
            engagement_timeline=dataset.engagement_timeline,
            most_active_accounts=dataset.most_active_accounts,
            most_valuable_accounts=dataset.most_valuable_accounts,
        )

    async def export_report(
        self,
        app_user_id: str,
        report_type: str,
        fmt: ExportFormat,
        filters: AnalyticsFilters,
    ) -> AnalyticsExportResponse:
        dataset = await self.get_dataset(app_user_id, filters)
        payload = {
            "filters": filters.model_dump(mode="json"),
            "report_type": report_type,
            "kpis": dataset.kpis.model_dump(mode="json"),
            "follower_growth": [point.model_dump(mode="json") for point in dataset.follower_growth],
            "engagement_timeline": [point.model_dump(mode="json") for point in dataset.engagement_timeline],
            "most_active_accounts": [item.model_dump(mode="json") for item in dataset.most_active_accounts],
            "most_valuable_accounts": [item.model_dump(mode="json") for item in dataset.most_valuable_accounts],
        }
        filename = f"analytics-{report_type}-{filters.end_date.isoformat()}.{fmt.value}"

        if fmt == ExportFormat.JSON:
            return AnalyticsExportResponse(
                format=fmt,
                filename=filename,
                content_type="application/json",
                content=json.dumps(payload, indent=2),
            )

        csv_content = self._to_csv(report_type, payload)
        return AnalyticsExportResponse(
            format=fmt,
            filename=filename,
            content_type="text/csv",
            content=csv_content,
        )

    def _to_csv(self, report_type: str, payload: dict) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["report_type", report_type])
        writer.writerow(["follow_back_rate", payload["kpis"]["follow_back_rate"]])
        writer.writerow(["average_follow_back_time_hours", payload["kpis"]["average_follow_back_time_hours"]])
        writer.writerow(["success_rate", payload["kpis"]["success_rate"]])
        writer.writerow([])
        writer.writerow(["follower_growth_label", "value"])
        for point in payload["follower_growth"]:
            writer.writerow([point["label"], point["value"]])
        writer.writerow([])
        writer.writerow(["engagement_timeline_label", "value"])
        for point in payload["engagement_timeline"]:
            writer.writerow([point["label"], point["value"]])
        writer.writerow([])
        writer.writerow(["account", "list_type", "follows", "follow_backs", "engagements", "value_score"])
        active_map = {item["account_id"]: item for item in payload["most_active_accounts"]}
        for value in payload["most_valuable_accounts"]:
            active = active_map.get(value["account_id"], {})
            writer.writerow([
                value["account"],
                value["list_type"],
                active.get("follows", 0),
                active.get("follow_backs", 0),
                active.get("engagements", 0),
                value["value_score"],
            ])
        return output.getvalue()

    async def _build_account_pool(self, app_user_id: str, filters: AnalyticsFilters) -> list[tuple[str, str, str]]:
        pools: list[tuple[str, str, str]] = []
        for list_type in WatchListType:
            try:
                entries = await self._watch_list_repository.list_entries(app_user_id, list_type)
            except Exception as exc:
                logger.warning("analytics_watchlist_unavailable", extra={"app_user_id": app_user_id, "list_type": list_type.value, "error": str(exc)})
                entries = []
            for entry in entries:
                pools.append((entry.x_user_id, entry.username, list_type.value))

        if filters.list_type:
            pools = [item for item in pools if item[2] == filters.list_type]
        if filters.account:
            needle = filters.account.lower()
            pools = [item for item in pools if needle in item[1].lower()]

        if pools:
            return pools[: max(self._settings.ANALYTICS_TOP_ACCOUNTS_LIMIT, 1)]

        seed = self._seed_for(app_user_id, filters)
        generated: list[tuple[str, str, str]] = []
        fallback_size = min(max(self._settings.ANALYTICS_TOP_ACCOUNTS_LIMIT, 3), 10)
        list_types = [t.value for t in WatchListType]
        for idx in range(fallback_size):
            user_num = 1000 + idx + seed.randint(1, 90)
            generated.append((f"acct-{user_num}", f"account_{user_num}", list_types[idx % len(list_types)]))
        return generated

    def _build_active_accounts(self, accounts: list[tuple[str, str, str]], seed: Random) -> list[ActiveAccountMetric]:
        items: list[ActiveAccountMetric] = []
        for account_id, username, list_type in accounts:
            follows = seed.randint(8, 90)
            follow_backs = min(follows, max(0, follows - seed.randint(0, 25)))
            engagements = seed.randint(3, 140)
            items.append(
                ActiveAccountMetric(
                    account_id=account_id,
                    account=username,
                    list_type=list_type,
                    follows=follows,
                    follow_backs=follow_backs,
                    engagements=engagements,
                )
            )
        items.sort(key=lambda x: (x.engagements, x.follow_backs, x.follows), reverse=True)
        return items[: self._settings.ANALYTICS_TOP_ACCOUNTS_LIMIT]

    def _build_valuable_accounts(
        self,
        active_accounts: list[ActiveAccountMetric],
        seed: Random,
    ) -> list[ValuableAccountMetric]:
        values: list[ValuableAccountMetric] = []
        for account in active_accounts:
            avg_time = round(3 + seed.random() * 62, 2)
            engagement_score = round(account.engagements / max(account.follows, 1), 3)
            value_score = round((account.follow_backs * 1.8) + (engagement_score * 4.1) - (avg_time * 0.15), 3)
            values.append(
                ValuableAccountMetric(
                    account_id=account.account_id,
                    account=account.account,
                    list_type=account.list_type,
                    value_score=max(0, value_score),
                    avg_follow_back_time_hours=avg_time,
                    engagement_score=engagement_score,
                )
            )
        values.sort(key=lambda x: x.value_score, reverse=True)
        return values[: self._settings.ANALYTICS_TOP_ACCOUNTS_LIMIT]

    def _series_for_filters(
        self,
        filters: AnalyticsFilters,
        baseline: int,
        seed: Random,
        floor: int,
    ) -> list[AnalyticsSeriesPoint]:
        steps: list[date] = []
        if filters.granularity == AnalyticsGranularity.DAILY:
            cursor = filters.start_date
            while cursor <= filters.end_date:
                steps.append(cursor)
                cursor += timedelta(days=1)
        elif filters.granularity == AnalyticsGranularity.WEEKLY:
            cursor = filters.start_date
            while cursor <= filters.end_date:
                steps.append(cursor)
                cursor += timedelta(days=7)
        else:
            cursor = date(filters.start_date.year, filters.start_date.month, 1)
            limit = date(filters.end_date.year, filters.end_date.month, 1)
            while cursor <= limit:
                steps.append(cursor)
                year = cursor.year + (cursor.month // 12)
                month = 1 if cursor.month == 12 else cursor.month + 1
                cursor = date(year, month, 1)

        value = baseline
        points: list[AnalyticsSeriesPoint] = []
        for step in steps[: self._settings.ANALYTICS_EXPORT_MAX_POINTS]:
            drift = seed.randint(-5, 22)
            value = max(floor, value + drift)
            if filters.granularity == AnalyticsGranularity.MONTHLY:
                label = step.strftime("%Y-%m")
            elif filters.granularity == AnalyticsGranularity.WEEKLY:
                label = f"W{step.isocalendar().week}"
            else:
                label = step.strftime("%m-%d")
            points.append(AnalyticsSeriesPoint(label=label, value=float(value)))
        return points

    def _seed_for(self, app_user_id: str, filters: AnalyticsFilters) -> Random:
        seed_input = f"{app_user_id}:{filters.start_date.isoformat()}:{filters.end_date.isoformat()}:{filters.list_type}:{filters.account}:{filters.granularity.value}"
        digest = hashlib.sha256(seed_input.encode("utf-8")).hexdigest()
        return Random(int(digest[:16], 16))

    @staticmethod
    def default_filters(
        start_date: date | None,
        end_date: date | None,
        list_type: str | None,
        account: str | None,
        granularity: AnalyticsGranularity,
    ) -> AnalyticsFilters:
        today = datetime.now(timezone.utc).date()
        effective_end = end_date or today
        effective_start = start_date or (effective_end - timedelta(days=30))
        if effective_start > effective_end:
            effective_start, effective_end = effective_end, effective_start
        return AnalyticsFilters(
            start_date=effective_start,
            end_date=effective_end,
            list_type=list_type,
            account=account,
            granularity=granularity,
        )

