"""Redis storage for processed tweets (notification prep)."""

from __future__ import annotations

from datetime import datetime, timezone

from app.infrastructure.redis.keys import RedisKeys, RedisTTL, get_redis_keys
from app.models.x.tweet import ProcessedTweetRecord
from app.repositories.redis_repository import RedisRepository


class ProcessedTweetRepository:
    def __init__(self, repository: RedisRepository, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()

    async def mark_processed(self, app_user_id: str, record: ProcessedTweetRecord) -> bool:
        key = self._keys.x_processed_tweet(app_user_id, record.tweet_id)
        payload = record.model_dump(mode="json")
        return await self._repository.set_json(key, payload, ex=RedisTTL.CACHE_LONG * 7)

    async def get(self, app_user_id: str, tweet_id: str) -> ProcessedTweetRecord | None:
        payload = await self._repository.get_json(self._keys.x_processed_tweet(app_user_id, tweet_id))
        if not payload:
            return None
        return ProcessedTweetRecord.model_validate(payload)

    async def is_processed(self, app_user_id: str, tweet_id: str) -> bool:
        return (await self._repository.exists(self._keys.x_processed_tweet(app_user_id, tweet_id))) > 0

    async def touch_pending(self, app_user_id: str, tweet_id: str, author_id: str) -> bool:
        record = ProcessedTweetRecord(
            tweet_id=tweet_id,
            author_id=author_id,
            processed_time=datetime.now(timezone.utc),
            notification_status="pending",
        )
        return await self.mark_processed(app_user_id, record)
