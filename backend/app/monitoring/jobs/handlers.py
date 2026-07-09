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
        return result.model_dump()

    return {
        JobType.POLL_FOLLOW_TARGETS: poll_follow_targets,
        JobType.POLL_FOLLOWING: poll_following,
        JobType.POLL_MUTUAL_FOLLOWERS: poll_mutual,
        JobType.SYNC_WATCH_LIST: sync_watch_list,
    }
