from __future__ import annotations

import logging

from app.core.config import Settings
from app.models.x.tweet import FilteredTweet
from app.notifications.service import NotificationService
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository

logger = logging.getLogger(__name__)


class NotificationJobs:
    def __init__(
        self,
        settings: Settings,
        processed_repo: ProcessedTweetRepository,
        notification_service: NotificationService,
    ) -> None:
        self._settings = settings
        self._processed_repo = processed_repo
        self._notification_service = notification_service

    async def process_pending(self, app_user_id: str, *, limit: int = 50) -> dict:
        pending = await self._processed_repo.list_pending(app_user_id, limit=limit)
        enqueued = 0
        skipped = 0
        for item in pending:
            record = item["record"]
            meta = item.get("meta") or {}
            list_type = meta.get("list_type", "following")
            created_at = record.tweet_created_at or record.processed_time
            url = record.url or f"https://x.com/i/web/status/{record.tweet_id}"
            tweet = FilteredTweet(
                tweet_id=record.tweet_id,
                author_id=record.author_id,
                username=record.username or record.author_id,
                text="",
                created_at=created_at,
                url=url,
            )
            ok = await self._notification_service.enqueue_tweet_notification(
                app_user_id,
                tweet,
                list_type=list_type,
            )
            if ok:
                enqueued += 1
            else:
                skipped += 1
        summary = {"app_user_id": app_user_id, "pending_scanned": len(pending), "enqueued": enqueued, "skipped": skipped}
        logger.info("notification_pending_processed", extra=summary)
        return summary
