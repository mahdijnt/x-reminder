from __future__ import annotations

import logging

from app.infrastructure.redis.user_cache import UserCache

logger = logging.getLogger(__name__)


class NotificationUserResolver:
    def __init__(self, user_cache: UserCache) -> None:
        self._user_cache = user_cache

    async def resolve_telegram_id(self, app_user_id: str) -> str | None:
        data = await self._user_cache.get_user(app_user_id)
        if not data:
            logger.warning("notification_user_not_cached", extra={"app_user_id": app_user_id})
            return None
        telegram_id = data.get("telegram_id") or data.get("telegram_chat_id")
        if not telegram_id:
            logger.warning("notification_telegram_id_missing", extra={"app_user_id": app_user_id})
            return None
        return str(telegram_id)
