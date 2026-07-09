from __future__ import annotations

import logging

from app.core.config import Settings
from app.infrastructure.redis.connection import RedisManager
from app.infrastructure.redis.user_cache import UserCache
from app.integrations.telegram.client import TelegramClient
from app.notifications.batch_processor import NotificationBatchProcessor
from app.notifications.dedup import NotificationDedupStore
from app.notifications.delivery_history import DeliveryHistoryStore
from app.notifications.failure_queue import NotificationFailureQueue
from app.notifications.jobs import NotificationJobs
from app.notifications.metrics import NotificationMetrics
from app.notifications.queue_manager import NotificationQueueManager
from app.notifications.rate_limiter import TelegramRateLimiter
from app.notifications.retry_queue import NotificationRetryQueue
from app.notifications.service import NotificationService
from app.notifications.telegram_delivery import TelegramDelivery
from app.notifications.user_resolver import NotificationUserResolver
from app.notifications.worker import NotificationWorker
from app.repositories.redis_repository import RedisRepository
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository

logger = logging.getLogger(__name__)


class NotificationEngine:
    def __init__(self, settings: Settings, repository: RedisRepository, redis_manager: RedisManager) -> None:
        self._settings = settings
        self._repository = repository
        self._metrics = NotificationMetrics(repository)
        self._queue = NotificationQueueManager(repository, settings)
        self._retry_queue = NotificationRetryQueue(repository, settings)
        self._failure_queue = NotificationFailureQueue(repository, settings)
        self._history = DeliveryHistoryStore(repository, settings)
        self._dedup = NotificationDedupStore(repository, settings)
        self._batch = NotificationBatchProcessor(settings)
        user_cache = UserCache(repository)
        self._user_resolver = NotificationUserResolver(user_cache)
        processed_repo = ProcessedTweetRepository(repository)
        self._service = NotificationService(
            settings,
            self._queue,
            self._batch,
            self._dedup,
            self._user_resolver,
            processed_repo,
            self._metrics,
            self._history,
        )
        self._jobs = NotificationJobs(settings, processed_repo, self._service)
        self._telegram_client = TelegramClient(settings)
        rate_limiter = TelegramRateLimiter(settings, redis_manager)
        delivery = TelegramDelivery(self._telegram_client, rate_limiter)
        self._worker = NotificationWorker(
            settings,
            self._queue,
            self._retry_queue,
            self._failure_queue,
            delivery,
            self._service,
            self._metrics,
        )

    @property
    def service(self) -> NotificationService:
        return self._service

    @property
    def jobs(self) -> NotificationJobs:
        return self._jobs

    @property
    def metrics(self) -> NotificationMetrics:
        return self._metrics

    @property
    def history(self) -> DeliveryHistoryStore:
        return self._history

    @property
    def worker(self) -> NotificationWorker:
        return self._worker

    def start(self) -> None:
        if not self._settings.NOTIFICATIONS_ENABLED:
            logger.info("notification_engine_disabled")
            return
        self._worker.start()
        logger.info("notification_engine_started")

    async def shutdown(self) -> None:
        if not self._settings.NOTIFICATIONS_ENABLED:
            return
        await self._batch.flush_all()
        await self._worker.stop()
        timeout = float(self._settings.NOTIFICATIONS_SHUTDOWN_TIMEOUT_SECONDS)
        idle = await self._worker.wait_idle(timeout)
        if not idle:
            logger.warning("notification_shutdown_timeout", extra={"in_flight": self._worker.in_flight})
        await self._telegram_client.close()
        logger.info("notification_engine_stopped")

    async def status(self) -> dict:
        depths = await self._queue.depth()
        retry_depth = await self._retry_queue.depth()
        failure_depth = await self._failure_queue.depth()
        await self._metrics.set_gauge("queue_depth", depths.get("total", 0))
        return {
            "enabled": self._settings.NOTIFICATIONS_ENABLED,
            "worker_enabled": self._settings.NOTIFICATIONS_WORKER_ENABLED,
            "worker_running": self._worker.running,
            "worker_in_flight": self._worker.in_flight,
            "queue_depth": depths,
            "retry_queue_depth": retry_depth,
            "failure_queue_depth": failure_depth,
            "metrics": await self._metrics.snapshot(),
            "telegram_configured": bool(self._settings.TELEGRAM_BOT_TOKEN.strip()),
        }
