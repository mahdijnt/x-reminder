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
