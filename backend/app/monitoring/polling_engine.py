from __future__ import annotations

import logging

from app.core.config import Settings
from app.models.x.watch_list import WatchListType
from app.monitoring.last_poll_store import LastPollStore
from app.monitoring.metrics import MonitoringMetrics
from app.monitoring.models import PollListType
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository
from app.services.watch_list_service import WatchListService
from app.models.x.tweet import FilteredTweet
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
        notification_service=None,
        tweet_memory_service=None,
    ) -> None:
        self._settings = settings
        self._tweet_service = tweet_service
        self._watch_list_service = watch_list_service
        self._processed_repo = processed_repo
        self._last_poll_store = last_poll_store
        self._metrics = metrics
        self._notification_service = notification_service
        self._tweet_memory_service = tweet_memory_service

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
                    await self._processed_repo.touch_pending(
                        app_user_id,
                        item.tweet_id,
                        item.author_id,
                        list_type=list_type.value,
                        username=item.username,
                        url=item.url,
                        tweet_created_at=item.created_at,
                    )
                    new_processed += 1
                    if self._tweet_memory_service is not None and self._settings.QDRANT_ENABLED:
                        from app.schemas.ai import TweetStoreRequest

                        await self._tweet_memory_service.store_tweet(
                            TweetStoreRequest(
                                tweet_id=item.tweet_id,
                                user_id=item.author_id,
                                text=item.text,
                                username=item.username,
                                created_at=item.created_at,
                            )
                        )

                    if self._notification_service is not None:
                        tweet = FilteredTweet(
                            tweet_id=item.tweet_id,
                            author_id=item.author_id,
                            username=item.username,
                            text=item.text,
                            created_at=item.created_at,
                            url=item.url,
                        )
                        await self._notification_service.enqueue_tweet_notification(
                            app_user_id,
                            tweet,
                            list_type=list_type.value,
                        )

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
