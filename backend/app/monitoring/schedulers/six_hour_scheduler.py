from __future__ import annotations

import logging

from app.core.config import Settings
from app.monitoring.models import JobType
from app.monitoring.task_manager import TaskManager

logger = logging.getLogger(__name__)


class SixHourScheduler:
    def __init__(self, settings: Settings, task_manager: TaskManager) -> None:
        self._settings = settings
        self._task_manager = task_manager

    async def tick(self) -> None:
        for app_user_id in self._settings.MONITORING_APP_USER_IDS:
            await self._task_manager.enqueue_job(JobType.POLL_FOLLOW_TARGETS, app_user_id)
            await self._task_manager.enqueue_job(JobType.POLL_MUTUAL_FOLLOWERS, app_user_id)
        logger.info(
            "monitoring_six_hour_tick",
            extra={"users": len(self._settings.MONITORING_APP_USER_IDS)},
        )

    @property
    def interval_minutes(self) -> int:
        return self._settings.MONITORING_SIX_HOUR_INTERVAL_MINUTES
