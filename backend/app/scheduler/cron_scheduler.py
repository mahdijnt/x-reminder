from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import Settings
from app.monitoring.schedulers.realtime_scheduler import RealtimeScheduler
from app.monitoring.schedulers.six_hour_scheduler import SixHourScheduler

logger = logging.getLogger(__name__)


class MonitoringCronScheduler:
    def __init__(
        self,
        settings: Settings,
        six_hour: SixHourScheduler,
        realtime: RealtimeScheduler,
    ) -> None:
        self._settings = settings
        self._six_hour = six_hour
        self._realtime = realtime
        self._scheduler = AsyncIOScheduler()

    def start(self) -> None:
        if not self._settings.MONITORING_ENABLED:
            logger.info("monitoring_cron_disabled")
            return
        self._scheduler.add_job(
            self._six_hour.tick,
            trigger="interval",
            minutes=self._six_hour.interval_minutes,
            id="monitoring_six_hour",
            replace_existing=True,
        )
        self._scheduler.add_job(
            self._realtime.tick,
            trigger="interval",
            seconds=self._realtime.interval_seconds,
            id="monitoring_realtime",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info("monitoring_cron_started")

    def shutdown(self, wait: bool = False) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=wait)

    @property
    def running(self) -> bool:
        return self._scheduler.running
