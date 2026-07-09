from __future__ import annotations

import logging

from app.core.config import Settings
from app.monitoring.models import JobType
from app.monitoring.task_manager import TaskManager

logger = logging.getLogger(__name__)


class RealtimeScheduler:
    def __init__(self, settings: Settings, task_manager: TaskManager) -> None:
        self._settings = settings
        self._task_manager = task_manager

    async def tick(self) -> None:
        for app_user_id in self._settings.MONITORING_APP_USER_IDS:
            await self._task_manager.enqueue_job(JobType.POLL_FOLLOWING, app_user_id, priority=1)
        logger.info(
            "monitoring_realtime_tick",
            extra={"users": len(self._settings.MONITORING_APP_USER_IDS)},
        )

    @property
    def interval_seconds(self) -> int:
        return self._settings.MONITORING_REALTIME_INTERVAL_SECONDS
