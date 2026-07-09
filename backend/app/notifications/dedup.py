from __future__ import annotations

import logging

from app.core.config import Settings
from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.repositories.redis_repository import RedisRepository

logger = logging.getLogger(__name__)


class NotificationDedupStore:
    def __init__(self, repository: RedisRepository, settings: Settings, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._settings = settings
        self._keys = keys or get_redis_keys()
        self._ttl = settings.NOTIFICATIONS_HISTORY_TTL_SECONDS

    async def try_claim(self, app_user_id: str, tweet_id: str) -> bool:
        key = self._keys.notifications_dedup(app_user_id, tweet_id)
        claimed = await self._repository.set(key, "1", nx=True, ex=self._ttl)
        if not claimed:
            logger.info(
                "notification_duplicate_skipped",
                extra={"app_user_id": app_user_id, "tweet_id": tweet_id},
            )
        return claimed

    async def is_notified(self, app_user_id: str, tweet_id: str) -> bool:
        key = self._keys.notifications_dedup(app_user_id, tweet_id)
        return (await self._repository.exists(key)) > 0
