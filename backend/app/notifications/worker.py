from __future__ import annotations

import asyncio
import logging
import time

from app.core.config import Settings
from app.integrations.telegram.client import TelegramAPIError
from app.notifications.failure_queue import NotificationFailureQueue
from app.notifications.metrics import NotificationMetrics
from app.notifications.models import DeliveryStatus
from app.notifications.queue_manager import NotificationQueueManager
from app.notifications.retry_queue import NotificationRetryQueue
from app.notifications.service import NotificationService
from app.notifications.telegram_delivery import TelegramDelivery

logger = logging.getLogger(__name__)


class NotificationWorker:
    def __init__(
        self,
        settings: Settings,
        queue: NotificationQueueManager,
        retry_queue: NotificationRetryQueue,
        failure_queue: NotificationFailureQueue,
        delivery: TelegramDelivery,
        service: NotificationService,
        metrics: NotificationMetrics,
    ) -> None:
        self._settings = settings
        self._queue = queue
        self._retry_queue = retry_queue
        self._failure_queue = failure_queue
        self._delivery = delivery
        self._service = service
        self._metrics = metrics
        self._tasks: list[asyncio.Task] = []
        self._stop = asyncio.Event()
        self._in_flight = 0

    @property
    def running(self) -> bool:
        return bool(self._tasks)

    @property
    def in_flight(self) -> int:
        return self._in_flight

    def start(self) -> None:
        if not self._settings.NOTIFICATIONS_WORKER_ENABLED:
            logger.info("notification_worker_disabled")
            return
        concurrency = max(1, self._settings.NOTIFICATIONS_WORKER_CONCURRENCY)
        for idx in range(concurrency):
            self._tasks.append(asyncio.create_task(self._loop(idx), name=f"notification-worker-{idx}"))
        logger.info("notification_workers_started", extra={"concurrency": concurrency})

    async def stop(self) -> None:
        self._stop.set()
        if self._tasks:
            await asyncio.wait(self._tasks, timeout=float(self._settings.NOTIFICATIONS_SHUTDOWN_TIMEOUT_SECONDS))
        for task in self._tasks:
            if not task.done():
                task.cancel()
        self._tasks.clear()

    async def wait_idle(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while self._in_flight > 0 and time.monotonic() < deadline:
            await asyncio.sleep(0.1)
        return self._in_flight == 0

    async def drain_retries(self) -> None:
        for payload in await self._retry_queue.poll_ready():
            await self._metrics.incr("notification_retries")
            await self._queue.enqueue(payload)

    async def _loop(self, worker_id: int) -> None:
        while not self._stop.is_set():
            await self.drain_retries()
            payload = await self._queue.dequeue()
            if payload is None:
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=1.0)
                except asyncio.TimeoutError:
                    pass
                continue
            self._in_flight += 1
            try:
                await self._process(payload)
            finally:
                self._in_flight -= 1

    async def _process(self, payload) -> None:
        claimed = await self._service.claim_for_delivery(payload)
        if claimed is None:
            logger.info("notification_job_skipped_duplicate", extra={"job_id": payload.job_id})
            return
        payload = claimed
        try:
            await self._delivery.deliver(payload)
            await self._service.record_delivery(payload, status=DeliveryStatus.SENT)
            await self._metrics.incr("notifications_sent", amount=len(payload.tweets))
        except TelegramAPIError as exc:
            await self._handle_failure(payload, str(exc))
        except Exception as exc:
            await self._handle_failure(payload, str(exc))

    async def _handle_failure(self, payload, error: str) -> None:
        logger.warning(
            "notification_delivery_failed",
            extra={"job_id": payload.job_id, "error": error, "attempt": payload.attempt},
        )
        scheduled = await self._retry_queue.schedule(payload, error)
        if scheduled:
            return
        await self._failure_queue.push(payload, error)
        await self._service.record_delivery(payload, status=DeliveryStatus.FAILED, error=error)
        await self._metrics.incr("notifications_failed", amount=len(payload.tweets))
