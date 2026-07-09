from __future__ import annotations

import logging

from app.core.config import Settings
from app.infrastructure.x.rate_limit_state import XRateLimitStateStore
from app.infrastructure.x.token_store import XTokenStore
from app.monitoring.job_history import JobHistoryStore
from app.monitoring.jobs.handlers import build_handlers
from app.monitoring.last_poll_store import LastPollStore
from app.monitoring.metrics import MonitoringMetrics
from app.monitoring.polling_engine import PollingEngine
from app.monitoring.queue_manager import QueueManager
from app.monitoring.retry_queue import RetryQueue
from app.monitoring.schedulers.realtime_scheduler import RealtimeScheduler
from app.monitoring.schedulers.six_hour_scheduler import SixHourScheduler
from app.monitoring.task_manager import TaskManager
from app.monitoring.workers.worker import MonitoringWorker
from app.repositories.redis_repository import RedisRepository
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository
from app.repositories.x_profile_repository import XProfileRepository
from app.repositories.x_watch_list_repository import WatchListRepository
from app.scheduler.cron_scheduler import MonitoringCronScheduler
from app.services.watch_list_service import WatchListService
from app.services.x_profile_service import XProfileService
from app.services.x_relationship_service import XRelationshipService
from app.services.x_sync_service import XSyncService
from app.services.x_token_service import XTokenService
from app.services.x_tweet_service import XTweetService

logger = logging.getLogger(__name__)


class MonitoringEngine:
    def __init__(self, settings: Settings, repository: RedisRepository, notification_service=None) -> None:
        self._settings = settings
        self._repository = repository
        self._metrics = MonitoringMetrics(repository)
        self._queue = QueueManager(repository, settings)
        self._retry_queue = RetryQueue(repository, settings)
        self._history = JobHistoryStore(repository, settings)
        self._last_poll = LastPollStore(repository)

        token_store = XTokenStore(repository, settings)
        token_service = XTokenService(settings, token_store)
        rate_limit_store = XRateLimitStateStore(repository)
        processed_repo = ProcessedTweetRepository(repository)
        watch_repo = WatchListRepository(repository)
        profile_repo = XProfileRepository(repository)

        tweet_service = XTweetService(settings, token_service, rate_limit_store, processed_repo)
        watch_list_service = WatchListService(watch_repo)
        profile_service = XProfileService(settings, token_service, profile_repo, rate_limit_store)
        relationship_service = XRelationshipService(settings, token_service, rate_limit_store)
        sync_service = XSyncService(
            settings,
            token_service,
            profile_service,
            relationship_service,
            profile_repo,
            watch_repo,
        )

        polling_engine = PollingEngine(
            settings,
            tweet_service,
            watch_list_service,
            processed_repo,
            self._last_poll,
            self._metrics,
            notification_service=notification_service,
        )
        handlers = build_handlers(polling_engine, sync_service)
        self._task_manager = TaskManager(self._queue, self._retry_queue, self._history, self._metrics, handlers)
        self._six_hour = SixHourScheduler(settings, self._task_manager)
        self._realtime = RealtimeScheduler(settings, self._task_manager)
        self._cron = MonitoringCronScheduler(settings, self._six_hour, self._realtime)
        self._worker = MonitoringWorker(settings, self._queue, self._task_manager)

    @property
    def task_manager(self) -> TaskManager:
        return self._task_manager

    @property
    def metrics(self) -> MonitoringMetrics:
        return self._metrics

    @property
    def history(self) -> JobHistoryStore:
        return self._history

    @property
    def last_poll_store(self) -> LastPollStore:
        return self._last_poll

    @property
    def cron_scheduler(self) -> MonitoringCronScheduler:
        return self._cron

    @property
    def worker(self) -> MonitoringWorker:
        return self._worker

    def start(self) -> None:
        if not self._settings.MONITORING_ENABLED:
            logger.info("monitoring_engine_disabled")
            return
        self._cron.start()
        self._worker.start()
        logger.info("monitoring_engine_started")

    async def shutdown(self) -> None:
        if not self._settings.MONITORING_ENABLED:
            return
        self._cron.shutdown(wait=False)
        await self._worker.stop()
        timeout = float(self._settings.MONITORING_SHUTDOWN_TIMEOUT_SECONDS)
        idle = await self._worker.wait_idle(timeout)
        if not idle:
            logger.warning("monitoring_shutdown_timeout", extra={"in_flight": self._worker.in_flight})
        logger.info("monitoring_engine_stopped")

    async def status(self) -> dict:
        depth = await self._queue.depth()
        retry_depth = await self._retry_queue.depth()
        await self._metrics.set_gauge("queue_depth", depth)
        return {
            "enabled": self._settings.MONITORING_ENABLED,
            "scheduler_running": self._cron.running,
            "worker_running": self._worker.running,
            "worker_in_flight": self._worker.in_flight,
            "queue_depth": depth,
            "retry_queue_depth": retry_depth,
            "metrics": await self._metrics.snapshot(),
        }
