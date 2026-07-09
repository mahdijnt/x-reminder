from __future__ import annotations

import asyncio
import logging
import time

from app.core.config import Settings
from app.infrastructure.redis.connection import RedisManager
from app.infrastructure.redis.rate_limit_store import RedisRateLimitStore

logger = logging.getLogger(__name__)


class TelegramRateLimiter:
    """Per-chat and global Telegram send rate limiting."""

    def __init__(self, settings: Settings, manager: RedisManager) -> None:
        self._settings = settings
        self._store = RedisRateLimitStore(manager)

    async def acquire(self, chat_id: str) -> None:
        per_chat = max(1, int(self._settings.NOTIFICATIONS_TELEGRAM_RATE_PER_CHAT))
        global_rate = max(1, int(self._settings.NOTIFICATIONS_TELEGRAM_RATE_GLOBAL))
        chat_key = f"telegram:chat:{chat_id}"
        global_key = "telegram:global"
        while True:
            chat_ok = await self._store.is_allowed(chat_key, limit=per_chat, window_seconds=1)
            global_ok = await self._store.is_allowed(global_key, limit=global_rate, window_seconds=1)
            if chat_ok and global_ok:
                return
            logger.debug(
                "notification_rate_limited",
                extra={"chat_id": chat_id, "chat_ok": chat_ok, "global_ok": global_ok},
            )
            await asyncio.sleep(0.05)
