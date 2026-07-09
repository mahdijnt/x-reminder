from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import Settings
from app.models.x.tweet import FilteredTweet
from app.notifications.batch_processor import NotificationBatchProcessor
from app.notifications.dedup import NotificationDedupStore
from app.notifications.metrics import NotificationMetrics
from app.notifications.models import (
    DeliveryChannel,
    DeliveryHistoryRecord,
    DeliveryStatus,
    NotificationJobPayload,
    NotificationPriority,
    TweetNotificationData,
)
from app.notifications.queue_manager import NotificationQueueManager
from app.notifications.user_resolver import NotificationUserResolver
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository

logger = logging.getLogger(__name__)

_LIST_PRIORITY = {
    "following": NotificationPriority.HIGH,
    "follow-targets": NotificationPriority.NORMAL,
    "mutual-followers": NotificationPriority.NORMAL,
}


class NotificationService:
    def __init__(
        self,
        settings: Settings,
        queue: NotificationQueueManager,
        batch_processor: NotificationBatchProcessor,
        dedup: NotificationDedupStore,
        user_resolver: NotificationUserResolver,
        processed_repo: ProcessedTweetRepository,
        metrics: NotificationMetrics,
        history,
    ) -> None:
        self._settings = settings
        self._queue = queue
        self._batch = batch_processor
        self._dedup = dedup
        self._user_resolver = user_resolver
        self._processed_repo = processed_repo
        self._metrics = metrics
        self._history = history
        self._batch.set_enqueue_callback(self._enqueue_payload)

    async def _enqueue_payload(self, payload: NotificationJobPayload) -> None:
        await self._queue.enqueue(payload)

    def priority_for_list(self, list_type: str) -> NotificationPriority:
        return _LIST_PRIORITY.get(list_type, NotificationPriority.LOW)

    async def enqueue_tweet_notification(
        self,
        app_user_id: str,
        tweet: FilteredTweet,
        *,
        list_type: str,
    ) -> bool:
        if not self._settings.NOTIFICATIONS_ENABLED:
            return False
        record = await self._processed_repo.get(app_user_id, tweet.tweet_id)
        if record and record.notification_status in {"sent", "skipped"}:
            await self._metrics.incr("notifications_skipped")
            return False
        if await self._dedup.is_notified(app_user_id, tweet.tweet_id):
            await self._metrics.incr("notifications_skipped")
            await self._processed_repo.set_notification_status(app_user_id, tweet.tweet_id, "skipped")
            return False
        telegram_id = await self._user_resolver.resolve_telegram_id(app_user_id)
        if not telegram_id:
            await self._metrics.incr("notifications_skipped")
            await self._processed_repo.set_notification_status(app_user_id, tweet.tweet_id, "failed")
            return False
        data = TweetNotificationData(
            tweet_id=tweet.tweet_id,
            author_id=tweet.author_id,
            username=tweet.username,
            url=tweet.url,
            created_at=tweet.created_at,
            list_type=list_type,
        )
        priority = self.priority_for_list(list_type)
        await self._batch.add(app_user_id, telegram_id, data, priority)
        return True

    async def enqueue_direct(self, payload: NotificationJobPayload) -> bool:
        return await self._queue.enqueue(payload)

    async def claim_for_delivery(self, payload: NotificationJobPayload) -> NotificationJobPayload | None:
        tweets: list[TweetNotificationData] = []
        for tweet in payload.tweets:
            if await self._dedup.try_claim(payload.app_user_id, tweet.tweet_id):
                tweets.append(tweet)
            else:
                await self._metrics.incr("notifications_skipped")
                await self._processed_repo.set_notification_status(payload.app_user_id, tweet.tweet_id, "skipped")
        if not tweets:
            return None
        payload.tweets = tweets
        return payload

    async def record_delivery(
        self,
        payload: NotificationJobPayload,
        *,
        status: DeliveryStatus,
        error: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        for tweet in payload.tweets:
            await self._history.record(
                DeliveryHistoryRecord(
                    notification_id=str(uuid4()),
                    app_user_id=payload.app_user_id,
                    tweet_id=tweet.tweet_id,
                    channel=DeliveryChannel.TELEGRAM,
                    status=status,
                    sent_at=now,
                    error=error,
                    telegram_id=payload.telegram_id,
                )
            )
            if status == DeliveryStatus.SENT:
                await self._processed_repo.set_notification_status(payload.app_user_id, tweet.tweet_id, "sent")
            elif status == DeliveryStatus.FAILED:
                await self._processed_repo.set_notification_status(payload.app_user_id, tweet.tweet_id, "failed")