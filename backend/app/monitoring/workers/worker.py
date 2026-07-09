from __future__ import annotations

import asyncio
import time
import logging

from app.core.config import Settings
from app.monitoring.queue_manager import QueueManager
from app.monitoring.task_manager import TaskManager

logger = logging.getLogger(__name__)


class MonitoringWorker:
    def __init__(
        self,
        settings: Settings,
        queue: QueueManager,
        task_manager: TaskManager,
    ) -> None:
        self._settings = settings
        self._queue = queue
        self._task_manager = task_manager
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
        if not self._settings.MONITORING_WORKER_ENABLED:
            logger.info("monitoring_worker_disabled")
            return
        concurrency = max(1, self._settings.MONITORING_WORKER_CONCURRENCY)
        for idx in range(concurrency):
            self._tasks.append(asyncio.create_task(self._loop(idx), name=f"monitoring-worker-{idx}"))
        logger.info("monitoring_workers_started", extra={"concurrency": concurrency})

    async def stop(self) -> None:
        self._stop.set()
        if self._tasks:
            await asyncio.wait(self._tasks, timeout=self._settings.MONITORING_SHUTDOWN_TIMEOUT_SECONDS)
        for task in self._tasks:
            if not task.done():
                task.cancel()
        self._tasks.clear()

    async def wait_idle(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while self._in_flight > 0 and time.monotonic() < deadline:
            await asyncio.sleep(0.1)
        return self._in_flight == 0

    async def _loop(self, worker_id: int) -> None:
        while not self._stop.is_set():
            await self._task_manager.drain_retries()
            payload = await self._queue.dequeue()
            if payload is None:
                try:
                    await asyncio.wait_for(self._stop.wait(), timeout=1.0)
                except asyncio.TimeoutError:
                    pass
                continue
            self._in_flight += 1
            try:
                await self._task_manager.execute_payload(payload)
            finally:
                self._in_flight -= 1

