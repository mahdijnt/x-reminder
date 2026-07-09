"""Scheduled X synchronization jobs (fetch/store only)."""

from __future__ import annotations

import logging
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import Settings
from app.services.x_sync_service import XSyncService

logger = logging.getLogger(__name__)


class XSyncScheduler:
    def __init__(self, settings: Settings, sync_service: XSyncService) -> None:
        self._settings = settings
        self._sync_service = sync_service
        self._scheduler = AsyncIOScheduler()

    def start(self) -> None:
        if not self._settings.X_SYNC_SCHEDULER_ENABLED:
            logger.info("x_sync_scheduler_disabled")
            return
        self._scheduler.add_job(
            self._run_scheduled_sync,
            trigger="interval",
            minutes=self._settings.X_SYNC_INTERVAL_MINUTES,
            id="x_periodic_sync",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info(
            "x_sync_scheduler_started",
            extra={"interval_minutes": self._settings.X_SYNC_INTERVAL_MINUTES},
        )

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    async def _run_scheduled_sync(self) -> None:
        for app_user_id in self._settings.X_SYNC_APP_USER_IDS:
            try:
                await self._sync_service.sync_account(app_user_id)
            except Exception as exc:
                logger.exception(
                    "x_scheduled_sync_failed",
                    extra={"app_user_id": app_user_id, "error": str(exc)},
                )

    async def sync_user_now(self, app_user_id: str) -> Any:
        return await self._sync_service.sync_account(app_user_id)
