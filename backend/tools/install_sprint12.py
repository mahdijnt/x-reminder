"""Generate Sprint 12 monitoring engine files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")
    print("wrote", rel)

# populated by append below

w("app/monitoring/models.py", r"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class JobType(str, Enum):
    POLL_FOLLOW_TARGETS = "poll_follow_targets"
    POLL_FOLLOWING = "poll_following"
    POLL_MUTUAL_FOLLOWERS = "poll_mutual_followers"
    SYNC_WATCH_LIST = "sync_watch_list"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class JobPayload(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    job_type: JobType
    app_user_id: str
    priority: int = 0
    attempt: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)
    enqueued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobRecord(BaseModel):
    job_id: str
    job_type: JobType
    status: JobStatus
    app_user_id: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    attempt: int = 1


class PollListType(str, Enum):
    FOLLOW_TARGETS = "follow-targets"
    FOLLOWING = "following"
    MUTUAL_FOLLOWERS = "mutual-followers"
""")

w("app/monitoring/__init__.py", r"""
from app.monitoring.monitoring_engine import MonitoringEngine

__all__ = ["MonitoringEngine"]
""")

w("app/monitoring/last_poll_store.py", r"""
from __future__ import annotations

from datetime import datetime, timezone

from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.repositories.redis_repository import RedisRepository


class LastPollStore:
    def __init__(self, repository: RedisRepository, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()

    async def get(self, app_user_id: str, list_type: str) -> datetime | None:
        raw = await self._repository.get(self._keys.monitoring_last_poll(app_user_id, list_type))
        if not raw:
            return None
        try:
            return datetime.fromisoformat(raw)
        except ValueError:
            return None

    async def set_now(self, app_user_id: str, list_type: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        return await self._repository.set(
            self._keys.monitoring_last_poll(app_user_id, list_type),
            now,
            ex=60 * 60 * 24 * 30,
        )
""")


w("app/monitoring/queue_manager.py", r"""
from __future__ import annotations

import json
import logging

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.monitoring.models import JobPayload
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class QueueManager:
    def __init__(self, repository: RedisRepository, settings: Settings, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()

    def _queue_key(self, priority: bool = False) -> str:
        base = self._settings.MONITORING_QUEUE_NAME
        if priority:
            return f"{base}:priority"
        return base

    async def enqueue(self, payload: JobPayload) -> bool:
        data = payload.model_dump(mode="json")
        body = json.dumps(data)
        use_priority = payload.priority > 0
        ok = await self._repository.rpush(self._queue_key(use_priority), body)
        if ok:
            logger.info(
                "monitoring_job_enqueued",
                extra={
                    "job_id": payload.job_id,
                    "job_type": payload.job_type.value,
                    "app_user_id": payload.app_user_id,
                    "priority": payload.priority,
                },
            )
        return ok

    async def dequeue(self) -> JobPayload | None:
        for priority in (True, False):
            raw = await self._repository.lpop(self._queue_key(priority))
            if raw:
                try:
                    return JobPayload.model_validate_json(raw)
                except Exception as exc:
                    logger.warning("monitoring_job_decode_failed", extra={"error": str(exc)})
        return None

    async def depth(self) -> int:
        return (await self._repository.llen(self._queue_key(True))) + (
            await self._repository.llen(self._queue_key(False))
        )
""")

w("app/monitoring/retry_queue.py", r"""
from __future__ import annotations

import json
import logging
import time

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.monitoring.models import JobPayload
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class RetryQueue:
    def __init__(self, repository: RedisRepository, settings: Settings, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()

    def _key(self) -> str:
        return self._keys.monitoring_retry()

    def _delay_seconds(self, attempt: int) -> int:
        base = self._settings.MONITORING_RETRY_BASE_DELAY_SECONDS
        return int(base * (2 ** max(0, attempt - 1)))

    async def schedule(self, payload: JobPayload, error: str) -> bool:
        if payload.attempt >= self._settings.MONITORING_RETRY_MAX_ATTEMPTS:
            logger.error(
                "monitoring_job_retry_exhausted",
                extra={"job_id": payload.job_id, "error": error},
            )
            return False
        payload.attempt += 1
        run_at = time.time() + self._delay_seconds(payload.attempt)
        body = json.dumps({"payload": payload.model_dump(mode="json"), "error": error})
        ok = await self._repository.zadd(self._key(), {body: run_at})
        if ok:
            logger.info(
                "monitoring_job_retry_scheduled",
                extra={"job_id": payload.job_id, "attempt": payload.attempt, "run_at": run_at},
            )
        return ok

    async def poll_ready(self, limit: int = 10) -> list[JobPayload]:
        now = time.time()
        items = await self._repository.zrangebyscore(self._key(), 0, now, start=0, num=limit)
        payloads: list[JobPayload] = []
        for body in items:
            await self._repository.zrem(self._key(), body)
            try:
                data = json.loads(body)
                payloads.append(JobPayload.model_validate(data["payload"]))
            except Exception as exc:
                logger.warning("monitoring_retry_decode_failed", extra={"error": str(exc)})
        return payloads

    async def depth(self) -> int:
        return await self._repository.zcard(self._key())
""")


w("app/monitoring/job_history.py", r"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.monitoring.models import JobRecord, JobStatus
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class JobHistoryStore:
    def __init__(self, repository: RedisRepository, settings: Settings, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()
        self._ttl = settings.MONITORING_JOB_HISTORY_TTL_SECONDS

    async def save(self, record: JobRecord) -> bool:
        key = self._keys.monitoring_job(record.job_id)
        payload = record.model_dump(mode="json")
        ok = await self._repository.set_json(key, payload, ex=self._ttl)
        score = (record.completed_at or record.started_at or datetime.now(timezone.utc)).timestamp()
        await self._repository.zadd(self._keys.monitoring_job_index(), {record.job_id: score})
        return ok

    async def get(self, job_id: str) -> JobRecord | None:
        data = await self._repository.get_json(self._keys.monitoring_job(job_id))
        if not data:
            return None
        return JobRecord.model_validate(data)

    async def list_recent(self, limit: int = 50) -> list[JobRecord]:
        ids = await self._repository.zrevrange(self._keys.monitoring_job_index(), 0, limit - 1)
        records: list[JobRecord] = []
        for job_id in ids:
            rec = await self.get(job_id)
            if rec:
                records.append(rec)
        return records

    async def mark_started(self, record: JobRecord) -> JobRecord:
        record.status = JobStatus.RUNNING
        record.started_at = datetime.now(timezone.utc)
        await self.save(record)
        return record

    async def mark_completed(self, record: JobRecord) -> JobRecord:
        record.status = JobStatus.COMPLETED
        record.completed_at = datetime.now(timezone.utc)
        await self.save(record)
        return record

    async def mark_failed(self, record: JobRecord, error: str) -> JobRecord:
        record.status = JobStatus.FAILED
        record.error = error
        record.completed_at = datetime.now(timezone.utc)
        await self.save(record)
        return record
""")

w("app/monitoring/metrics.py", r"""
from __future__ import annotations

import logging

from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)

METRIC_KEYS = (
    "jobs_processed",
    "jobs_failed",
    "tweets_fetched",
    "duplicates_skipped",
)


class MonitoringMetrics:
    def __init__(self, repository: RedisRepository, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()
        self._local: dict[str, int] = {k: 0 for k in METRIC_KEYS}
        self._local["queue_depth"] = 0

    def _hash_key(self) -> str:
        return self._keys.monitoring_metrics()

    async def incr(self, name: str, amount: int = 1) -> None:
        if name in self._local:
            self._local[name] += amount
        await self._repository.hincrby(self._hash_key(), name, amount)

    async def set_gauge(self, name: str, value: int) -> None:
        self._local[name] = value
        await self._repository.hset(self._hash_key(), name, str(value))

    async def snapshot(self) -> dict[str, int]:
        raw = await self._repository.hgetall(self._hash_key())
        merged = dict(self._local)
        for k, v in raw.items():
            try:
                merged[k] = int(v)
            except ValueError:
                continue
        return merged

    def prometheus_text(self, data: dict[str, int]) -> str:
        lines = []
        for key, value in sorted(data.items()):
            lines.append(f"monitoring_{key} {value}")
        return "\n".join(lines) + "\n"
""")


w("app/monitoring/polling_engine.py", r"""
from __future__ import annotations

import logging

from app.core.config import Settings
from app.models.x.watch_list import WatchListType
from app.monitoring.last_poll_store import LastPollStore
from app.monitoring.metrics import MonitoringMetrics
from app.monitoring.models import PollListType
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository
from app.services.watch_list_service import WatchListService
from app.services.x_tweet_service import XTweetService

logger = logging.getLogger(__name__)

_LIST_MAP = {
    PollListType.FOLLOW_TARGETS: WatchListType.FOLLOW_TARGETS,
    PollListType.FOLLOWING: WatchListType.FOLLOWING,
    PollListType.MUTUAL_FOLLOWERS: WatchListType.MUTUAL_FOLLOWERS,
}


class PollingEngine:
    def __init__(
        self,
        settings: Settings,
        tweet_service: XTweetService,
        watch_list_service: WatchListService,
        processed_repo: ProcessedTweetRepository,
        last_poll_store: LastPollStore,
        metrics: MonitoringMetrics,
    ) -> None:
        self._settings = settings
        self._tweet_service = tweet_service
        self._watch_list_service = watch_list_service
        self._processed_repo = processed_repo
        self._last_poll_store = last_poll_store
        self._metrics = metrics

    async def _entries_for(self, app_user_id: str, list_type: PollListType):
        if list_type == PollListType.FOLLOW_TARGETS:
            resp = await self._watch_list_service.list_follow_targets(app_user_id)
        elif list_type == PollListType.FOLLOWING:
            resp = await self._watch_list_service.list_following(app_user_id)
        else:
            resp = await self._watch_list_service.list_mutual_followers(app_user_id)
        return resp.items

    async def poll_list(self, app_user_id: str, list_type: PollListType) -> dict:
        entries = await self._entries_for(app_user_id, list_type)
        batch_size = self._settings.MONITORING_POLL_BATCH_SIZE
        tweets_fetched = 0
        duplicates_skipped = 0
        new_processed = 0

        for entry in entries[:batch_size]:
            page_token = None
            while True:
                result = await self._tweet_service.fetch_user_tweets(
                    app_user_id,
                    entry.x_user_id,
                    pagination_token=page_token,
                    record_processed=False,
                )
                for item in result.items:
                    tweets_fetched += 1
                    if await self._processed_repo.is_processed(app_user_id, item.tweet_id):
                        duplicates_skipped += 1
                        logger.info(
                            "monitoring_duplicate_skipped",
                            extra={
                                "app_user_id": app_user_id,
                                "tweet_id": item.tweet_id,
                                "list_type": list_type.value,
                            },
                        )
                        continue
                    await self._processed_repo.touch_pending(app_user_id, item.tweet_id, item.author_id)
                    new_processed += 1

                page_token = result.next_token
                if not page_token:
                    break

        await self._last_poll_store.set_now(app_user_id, list_type.value)
        await self._metrics.incr("tweets_fetched", tweets_fetched)
        await self._metrics.incr("duplicates_skipped", duplicates_skipped)

        summary = {
            "list_type": list_type.value,
            "accounts_scanned": min(len(entries), batch_size),
            "tweets_fetched": tweets_fetched,
            "duplicates_skipped": duplicates_skipped,
            "new_processed": new_processed,
        }
        logger.info("monitoring_poll_complete", extra={"app_user_id": app_user_id, **summary})
        return summary
""")

w("app/monitoring/jobs/__init__.py", r"""
from app.monitoring.jobs.handlers import JOB_HANDLERS

__all__ = ["JOB_HANDLERS"]
""")

w("app/monitoring/jobs/handlers.py", r"""
from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.monitoring.models import JobPayload, JobType, PollListType
from app.monitoring.polling_engine import PollingEngine
from app.services.x_sync_service import XSyncService

JobHandler = Callable[[JobPayload], Awaitable[dict]]


def build_handlers(polling_engine: PollingEngine, sync_service: XSyncService) -> dict[JobType, JobHandler]:
    async def poll_follow_targets(payload: JobPayload) -> dict:
        return await polling_engine.poll_list(payload.app_user_id, PollListType.FOLLOW_TARGETS)

    async def poll_following(payload: JobPayload) -> dict:
        return await polling_engine.poll_list(payload.app_user_id, PollListType.FOLLOWING)

    async def poll_mutual(payload: JobPayload) -> dict:
        return await polling_engine.poll_list(payload.app_user_id, PollListType.MUTUAL_FOLLOWERS)

    async def sync_watch_list(payload: JobPayload) -> dict:
        result = await sync_service.sync_account(payload.app_user_id)
        return {"synced": True, "detail": getattr(result, "model_dump", lambda **k: str(result))()}

    return {
        JobType.POLL_FOLLOW_TARGETS: poll_follow_targets,
        JobType.POLL_FOLLOWING: poll_following,
        JobType.POLL_MUTUAL_FOLLOWERS: poll_mutual,
        JobType.SYNC_WATCH_LIST: sync_watch_list,
    }
""")


w("app/monitoring/task_manager.py", r"""
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
""")

w("app/monitoring/workers/__init__.py", r"""
from app.monitoring.workers.worker import MonitoringWorker

__all__ = ["MonitoringWorker"]
""")

w("app/monitoring/workers/worker.py", r"""
from __future__ import annotations

import asyncio
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
        deadline = asyncio.get_event_loop().time() + timeout
        while self._in_flight > 0 and asyncio.get_event_loop().time() < deadline:
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
""")


w("app/monitoring/schedulers/__init__.py", r"""
from app.monitoring.schedulers.realtime_scheduler import RealtimeScheduler
from app.monitoring.schedulers.six_hour_scheduler import SixHourScheduler

__all__ = ["SixHourScheduler", "RealtimeScheduler"]
""")

w("app/monitoring/schedulers/six_hour_scheduler.py", r"""
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
""")

w("app/monitoring/schedulers/realtime_scheduler.py", r"""
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
""")

w("app/scheduler/cron_scheduler.py", r"""
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
""")


w("app/monitoring/monitoring_engine.py", r"""
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
    def __init__(self, settings: Settings, repository: RedisRepository) -> None:
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
""")

w("app/monitoring/health.py", r"""
from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import Settings
from app.monitoring.monitoring_engine import MonitoringEngine
from app.monitoring.models import PollListType


async def monitoring_health(settings: Settings, engine: MonitoringEngine | None) -> dict:
    if not settings.MONITORING_ENABLED:
        return {"status": "disabled", "detail": "MONITORING_ENABLED=false"}
    if engine is None:
        return {"status": "unavailable", "detail": "Monitoring engine not initialized"}
    status = await engine.status()
    last_polls = {}
    for list_type in PollListType:
        for user_id in settings.MONITORING_APP_USER_IDS:
            ts = await engine.last_poll_store.get(user_id, list_type.value)
            last_polls[f"{user_id}:{list_type.value}"] = ts.isoformat() if ts else None
    overall = "ok" if status.get("scheduler_running") and status.get("worker_running") else "degraded"
    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engine": status,
        "last_successful_poll": last_polls,
    }
""")

w("app/monitoring/worker_main.py", r"""\n# Standalone monitoring worker entry point.

import asyncio
import logging

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.redis.connection import get_redis_manager
from app.monitoring.monitoring_engine import MonitoringEngine
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


async def _run() -> None:
    settings = get_settings()
    configure_logging(settings)
    manager = get_redis_manager(settings)
    await manager.connect()
    engine = MonitoringEngine(settings, RedisRepository(manager))
    engine.start()
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await engine.shutdown()
        await manager.disconnect()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
""")


w("app/schemas/monitoring.py", r"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.monitoring.models import JobRecord, JobType


class MonitoringStatusData(BaseModel):
    enabled: bool
    scheduler_running: bool
    worker_running: bool
    worker_in_flight: int
    queue_depth: int
    retry_queue_depth: int
    metrics: dict[str, int]


class MonitoringHealthData(BaseModel):
    status: str
    timestamp: datetime
    engine: dict[str, Any]
    last_successful_poll: dict[str, str | None]


class JobHistoryListData(BaseModel):
    items: list[JobRecord]


class TriggerJobRequest(BaseModel):
    app_user_id: str | None = None


class TriggerJobData(BaseModel):
    job_id: str
    job_type: JobType
    app_user_id: str
""")

w("app/api/v1/endpoints/monitoring.py", r"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from app.core.auth_context import AppUserIdDep
from app.core.config import SettingsDep
from app.core.dependencies import get_settings
from app.monitoring.models import JobType
from app.schemas.monitoring import (
    JobHistoryListData,
    MonitoringHealthData,
    MonitoringStatusData,
    TriggerJobData,
)
from app.schemas.responses import APIResponse

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def _engine(request: Request):
    return getattr(request.app.state, "monitoring_engine", None)


@router.get("/status", response_model=APIResponse[MonitoringStatusData])
async def monitoring_status(request: Request, settings: SettingsDep) -> APIResponse[MonitoringStatusData]:
    engine = _engine(request)
    if not settings.MONITORING_ENABLED or engine is None:
        data = MonitoringStatusData(
            enabled=False,
            scheduler_running=False,
            worker_running=False,
            worker_in_flight=0,
            queue_depth=0,
            retry_queue_depth=0,
            metrics={},
        )
        return APIResponse.ok(data=data, message="Monitoring disabled")
    raw = await engine.status()
    return APIResponse.ok(data=MonitoringStatusData(**raw))


@router.get("/health", response_model=APIResponse[dict])
async def monitoring_health_endpoint(request: Request, settings: SettingsDep) -> APIResponse[dict]:
    from app.monitoring.health import monitoring_health

    engine = _engine(request)
    data = await monitoring_health(settings, engine)
    return APIResponse.ok(data=data)


@router.get("/jobs", response_model=APIResponse[JobHistoryListData])
async def monitoring_jobs(request: Request, settings: SettingsDep, limit: int = 50) -> APIResponse[JobHistoryListData]:
    engine = _engine(request)
    if not settings.MONITORING_ENABLED or engine is None:
        return APIResponse.ok(data=JobHistoryListData(items=[]), message="Monitoring disabled")
    items = await engine.history.list_recent(limit=limit)
    return APIResponse.ok(data=JobHistoryListData(items=items))


@router.get("/metrics")
async def monitoring_metrics(request: Request, settings: SettingsDep, format: str = "json"):
    engine = _engine(request)
    if not settings.MONITORING_ENABLED or engine is None:
        if format == "prometheus":
            return PlainTextResponse("")
        return APIResponse.ok(data={})
    data = await engine.metrics.snapshot()
    if format == "prometheus":
        return PlainTextResponse(engine.metrics.prometheus_text(data), media_type="text/plain")
    return APIResponse.ok(data=data)


@router.post("/trigger/{job_type}", response_model=APIResponse[TriggerJobData])
async def trigger_job(
    job_type: JobType,
    request: Request,
    settings: SettingsDep,
    app_user_id: AppUserIdDep,
) -> APIResponse[TriggerJobData]:
    engine = _engine(request)
    if not settings.MONITORING_ENABLED or engine is None:
        return APIResponse.fail(message="Monitoring disabled", code="monitoring_disabled")
    payload = await engine.task_manager.enqueue_job(job_type, app_user_id, priority=2)
    data = TriggerJobData(job_id=payload.job_id, job_type=payload.job_type, app_user_id=payload.app_user_id)
    return APIResponse.ok(data=data, message="Job enqueued")
""")


def patch_redis_repository() -> None:
    path = ROOT / "app/repositories/redis_repository.py"
    text = path.read_text(encoding="utf-8")
    if "async def rpush" in text:
        return
    insert = '''

    async def rpush(self, key: str, value: str) -> bool:
        async def _op(client: Redis) -> bool:
            await client.rpush(key, value)
            return True

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return False

    async def lpop(self, key: str) -> str | None:
        async def _op(client: Redis) -> str | None:
            return await client.lpop(key)

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return None

    async def llen(self, key: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.llen(key))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def zadd(self, key: str, mapping: dict[str, float]) -> bool:
        async def _op(client: Redis) -> bool:
            await client.zadd(key, mapping)
            return True

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return False

    async def zrem(self, key: str, member: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.zrem(key, member))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def zrangebyscore(
        self,
        key: str,
        min_score: float,
        max_score: float,
        *,
        start: int = 0,
        num: int = -1,
    ) -> list[str]:
        async def _op(client: Redis) -> list[str]:
            return list(await client.zrangebyscore(key, min_score, max_score, start=start, num=num))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return []

    async def zcard(self, key: str) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.zcard(key))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0

    async def zrevrange(self, key: str, start: int, end: int) -> list[str]:
        async def _op(client: Redis) -> list[str]:
            return list(await client.zrevrange(key, start, end))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return []

    async def hincrby(self, name: str, key: str, amount: int = 1) -> int:
        async def _op(client: Redis) -> int:
            return int(await client.hincrby(name, key, amount))

        try:
            return await self._manager.execute(_op)
        except (RedisUnavailableError, RedisConnectionError):
            return 0
'''
    marker = "    async def set_json(self, key: str, value: Any, *, ex: int | None = None) -> bool:"
    if marker not in text:
        raise SystemExit("redis_repository patch marker missing")
    text = text.replace(
        "    async def set_json(self, key: str, value: Any, *, ex: int | None = None) -> bool:\n        return await self.set(key, json.dumps(value), ex=ex)",
        "    async def set_json(self, key: str, value: Any, *, ex: int | None = None) -> bool:\n        return await self.set(key, json.dumps(value), ex=ex)" + insert,
    )
    path.write_text(text, encoding="utf-8")
    print("patched redis_repository")


def patch_keys() -> None:
    path = ROOT / "app/infrastructure/redis/keys.py"
    text = path.read_text(encoding="utf-8")
    if "monitoring_queue" in text:
        return
    block = '''
    def monitoring_queue(self) -> str:
        return self._key("monitoring", "queue")

    def monitoring_retry(self) -> str:
        return self._key("monitoring", "retry")

    def monitoring_job(self, job_id: str) -> str:
        return self._key("monitoring", "job", job_id)

    def monitoring_job_index(self) -> str:
        return self._key("monitoring", "job_index")

    def monitoring_metrics(self) -> str:
        return self._key("monitoring", "metrics")

    def monitoring_last_poll(self, app_user_id: str, list_type: str) -> str:
        return self._key("monitoring", "last_poll", app_user_id, list_type)
'''
    text = text.replace(
        "    def x_processed_tweet(self, app_user_id: str, tweet_id: str) -> str:\n        return self._key(\"x\", \"processed\", app_user_id, tweet_id)",
        "    def x_processed_tweet(self, app_user_id: str, tweet_id: str) -> str:\n        return self._key(\"x\", \"processed\", app_user_id, tweet_id)" + block,
    )
    path.write_text(text, encoding="utf-8")
    print("patched keys")


def patch_config() -> None:
    path = ROOT / "app/core/config.py"
    text = path.read_text(encoding="utf-8")
    if "MONITORING_ENABLED" in text:
        return
    insert = '''
    MONITORING_ENABLED: bool = False
    MONITORING_WORKER_ENABLED: bool = True
    MONITORING_SIX_HOUR_INTERVAL_MINUTES: int = 360
    MONITORING_REALTIME_INTERVAL_SECONDS: int = 120
    MONITORING_QUEUE_NAME: str = "monitoring:jobs"
    MONITORING_RETRY_MAX_ATTEMPTS: int = 5
    MONITORING_RETRY_BASE_DELAY_SECONDS: int = 30
    MONITORING_JOB_HISTORY_TTL_SECONDS: int = 604800
    MONITORING_WORKER_CONCURRENCY: int = 2
    MONITORING_SHUTDOWN_TIMEOUT_SECONDS: int = 30
    MONITORING_POLL_BATCH_SIZE: int = 50
    MONITORING_APP_USER_IDS: list[str] = Field(default_factory=list)
'''
    text = text.replace("    X_SYNC_APP_USER_IDS: list[str] = Field(default_factory=list)", "    X_SYNC_APP_USER_IDS: list[str] = Field(default_factory=list)" + insert)
    if "parse_monitoring_users" not in text:
        validator = '''
    @field_validator("MONITORING_APP_USER_IDS", mode="before")
    @classmethod
    def parse_monitoring_users(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

'''
        text = text.replace("    @field_validator(\"X_SYNC_APP_USER_IDS\", mode=\"before\")", validator + "    @field_validator(\"X_SYNC_APP_USER_IDS\", mode=\"before\")")
    path.write_text(text, encoding="utf-8")
    print("patched config")


def patch_router() -> None:
    path = ROOT / "app/api/v1/router.py"
    text = path.read_text(encoding="utf-8")
    if "monitoring" in text:
        return
    text = text.replace(
        "from app.api.v1.endpoints import auth_x, health, watch_lists, x_profile",
        "from app.api.v1.endpoints import auth_x, health, monitoring, watch_lists, x_profile",
    )
    text = text.replace(
        "api_router.include_router(watch_lists.router)",
        "api_router.include_router(watch_lists.router)\napi_router.include_router(monitoring.router)",
    )
    path.write_text(text, encoding="utf-8")
    print("patched router")


def patch_factory() -> None:
    path = ROOT / "app/factory.py"
    text = path.read_text(encoding="utf-8")
    if "monitoring_engine" in text:
        return
    text = text.replace(
        "    sync_scheduler = None\n    if settings.X_SYNC_SCHEDULER_ENABLED:",
        "    sync_scheduler = None\n    monitoring_engine = None\n    if settings.X_SYNC_SCHEDULER_ENABLED:",
    )
    block = '''
    if settings.MONITORING_ENABLED:
        from app.monitoring.monitoring_engine import MonitoringEngine
        from app.repositories.redis_repository import RedisRepository

        monitoring_engine = MonitoringEngine(settings, RedisRepository(redis_manager))
        monitoring_engine.start()
        app.state.monitoring_engine = monitoring_engine

'''
    text = text.replace("        app.state.x_sync_scheduler = sync_scheduler\n\n    yield", "        app.state.x_sync_scheduler = sync_scheduler\n" + block + "\n    yield")
    shutdown = '''
    if monitoring_engine is not None:
        await monitoring_engine.shutdown()

'''
    text = text.replace("    if sync_scheduler is not None:\n        sync_scheduler.shutdown()\n\n    await redis_manager.disconnect()", "    if sync_scheduler is not None:\n        sync_scheduler.shutdown()\n" + shutdown + "\n    await redis_manager.disconnect()")
    path.write_text(text, encoding="utf-8")
    print("patched factory")


def patch_env_example() -> None:
    path = ROOT.parent / ".env.example"
    text = path.read_text(encoding="utf-8")
    if "MONITORING_ENABLED" in text:
        return
    block = '''
MONITORING_ENABLED=true
MONITORING_WORKER_ENABLED=true
MONITORING_SIX_HOUR_INTERVAL_MINUTES=360
MONITORING_REALTIME_INTERVAL_SECONDS=120
MONITORING_QUEUE_NAME=monitoring:jobs
MONITORING_RETRY_MAX_ATTEMPTS=5
MONITORING_RETRY_BASE_DELAY_SECONDS=30
MONITORING_JOB_HISTORY_TTL_SECONDS=604800
MONITORING_WORKER_CONCURRENCY=2
MONITORING_SHUTDOWN_TIMEOUT_SECONDS=30
MONITORING_POLL_BATCH_SIZE=50
MONITORING_APP_USER_IDS=
'''
    path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")
    print("patched .env.example")


def patch_health_service() -> None:
    path = ROOT / "app/services/health_service.py"
    text = path.read_text(encoding="utf-8")
    if "monitoring_engine" in text:
        return
    text = text.replace(
        "        redis_manager: RedisManager | None = None,\n    ) -> None:",
        "        redis_manager: RedisManager | None = None,\n        monitoring_engine=None,\n    ) -> None:",
    )
    text = text.replace("        self._redis_manager = redis_manager", "        self._redis_manager = redis_manager\n        self._monitoring_engine = monitoring_engine")
    block = '''
        if self._settings.MONITORING_ENABLED:
            if self._monitoring_engine is None:
                checks["monitoring"] = HealthCheckItem(status="unavailable", detail="Engine not initialized")
                overall = "degraded" if overall == "ok" else overall
            else:
                status = await self._monitoring_engine.status()
                ok = status.get("scheduler_running") and status.get("worker_running")
                checks["monitoring"] = HealthCheckItem(
                    status="ok" if ok else "degraded",
                    detail=f"queue_depth={status.get('queue_depth', 0)}",
                )
                if not ok:
                    overall = "degraded"
        else:
            checks["monitoring"] = HealthCheckItem(status="disabled", detail="MONITORING_ENABLED=false")

'''
    text = text.replace(
        "        return HealthData(",
        block + "\n        return HealthData(",
    )
    path.write_text(text, encoding="utf-8")
    print("patched health_service")


def patch_dependencies() -> None:
    path = ROOT / "app/core/dependencies.py"
    text = path.read_text(encoding="utf-8")
    if "monitoring_engine" in text:
        return
    text = text.replace(
        "async def get_health_service(\n    settings: SettingsDep,\n    repository: Annotated[InMemoryRepository, Depends(get_health_repository)],\n    manager: RedisManagerDep,\n) -> AsyncGenerator[HealthService, None]:\n    yield HealthService(settings=settings, repository=repository, redis_manager=manager)",
        "def _monitoring_engine_from_request(request: Request):\n    return getattr(request.app.state, \"monitoring_engine\", None)\n\n\nasync def get_health_service(\n    request: Request,\n    settings: SettingsDep,\n    repository: Annotated[InMemoryRepository, Depends(get_health_repository)],\n    manager: RedisManagerDep,\n) -> AsyncGenerator[HealthService, None]:\n    yield HealthService(\n        settings=settings,\n        repository=repository,\n        redis_manager=manager,\n        monitoring_engine=_monitoring_engine_from_request(request),\n    )",
    )
    path.write_text(text, encoding="utf-8")
    print("patched dependencies")


if __name__ == "__main__":
    patch_redis_repository()
    patch_keys()
    patch_config()
    patch_router()
    patch_factory()
    patch_env_example()
    patch_health_service()
    patch_dependencies()
    print("done")
