from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.monitoring.job_history import JobHistoryStore
from app.monitoring.metrics import MonitoringMetrics
from app.monitoring.models import JobPayload, JobRecord, JobStatus, JobType
from app.monitoring.queue_manager import QueueManager
from app.monitoring.retry_queue import RetryQueue

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(
        self,
        queue: QueueManager,
        retry_queue: RetryQueue,
        history: JobHistoryStore,
        metrics: MonitoringMetrics,
        handlers: dict[JobType, object],
    ) -> None:
        self._queue = queue
        self._retry_queue = retry_queue
        self._history = history
        self._metrics = metrics
        self._handlers = handlers

    def _record_from_payload(self, payload: JobPayload) -> JobRecord:
        return JobRecord(
            job_id=payload.job_id,
            job_type=payload.job_type,
            status=JobStatus.PENDING,
            app_user_id=payload.app_user_id,
            metadata=payload.metadata,
            attempt=payload.attempt,
        )

    async def enqueue_job(
        self,
        job_type: JobType,
        app_user_id: str,
        *,
        priority: int = 0,
        metadata: dict | None = None,
    ) -> JobPayload:
        payload = JobPayload(
            job_type=job_type,
            app_user_id=app_user_id,
            priority=priority,
            metadata=metadata or {},
            enqueued_at=datetime.now(timezone.utc),
        )
        await self._history.save(self._record_from_payload(payload))
        await self._queue.enqueue(payload)
        depth = await self._queue.depth()
        await self._metrics.set_gauge("queue_depth", depth)
        return payload

    async def execute_payload(self, payload: JobPayload) -> dict:
        record = await self._history.mark_started(self._record_from_payload(payload))
        handler = self._handlers.get(payload.job_type)
        if handler is None:
            raise ValueError(f"No handler for job type {payload.job_type}")
        try:
            logger.info(
                "monitoring_job_started",
                extra={"job_id": payload.job_id, "job_type": payload.job_type.value},
            )
            result = await handler(payload)
            await self._history.mark_completed(record)
            await self._metrics.incr("jobs_processed")
            logger.info(
                "monitoring_job_completed",
                extra={"job_id": payload.job_id, "job_type": payload.job_type.value},
            )
            return result if isinstance(result, dict) else {"result": result}
        except Exception as exc:
            await self._history.mark_failed(record, str(exc))
            await self._metrics.incr("jobs_failed")
            logger.exception(
                "monitoring_job_failed",
                extra={"job_id": payload.job_id, "job_type": payload.job_type.value},
            )
            scheduled = await self._retry_queue.schedule(payload, str(exc))
            if not scheduled:
                raise
            return {"retry_scheduled": True, "error": str(exc)}

    async def drain_retries(self) -> int:
        moved = 0
        for payload in await self._retry_queue.poll_ready():
            await self._queue.enqueue(payload)
            moved += 1
        if moved:
            depth = await self._queue.depth()
            await self._metrics.set_gauge("queue_depth", depth)
        return moved
