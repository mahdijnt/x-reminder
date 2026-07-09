from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone

from app.core.config import Settings
from app.notifications.models import NotificationJobPayload, NotificationPriority, TweetNotificationData

logger = logging.getLogger(__name__)


class NotificationBatchProcessor:
  """Buffers tweets per user within a time window before enqueue."""

  def __init__(self, settings: Settings) -> None:
      self._settings = settings
      self._buffers: dict[str, list[TweetNotificationData]] = defaultdict(list)
      self._priorities: dict[str, NotificationPriority] = {}
      self._telegram_ids: dict[str, str] = {}
      self._flush_tasks: dict[str, asyncio.Task] = {}
      self._lock = asyncio.Lock()
      self._enqueue_cb = None

  def set_enqueue_callback(self, callback) -> None:
      self._enqueue_cb = callback

  async def add(
      self,
      app_user_id: str,
      telegram_id: str,
      tweet: TweetNotificationData,
      priority: NotificationPriority,
  ) -> None:
      async with self._lock:
          self._buffers[app_user_id].append(tweet)
          current = self._priorities.get(app_user_id, NotificationPriority.LOW)
          if _priority_rank(priority) > _priority_rank(current):
              self._priorities[app_user_id] = priority
          self._telegram_ids[app_user_id] = telegram_id
          if len(self._buffers[app_user_id]) >= self._settings.NOTIFICATIONS_BATCH_MAX_SIZE:
              await self._flush_user(app_user_id)
              return
          if app_user_id not in self._flush_tasks or self._flush_tasks[app_user_id].done():
              self._flush_tasks[app_user_id] = asyncio.create_task(self._delayed_flush(app_user_id))

  async def _delayed_flush(self, app_user_id: str) -> None:
      await asyncio.sleep(self._settings.NOTIFICATIONS_BATCH_WINDOW_SECONDS)
      async with self._lock:
          await self._flush_user(app_user_id)

  async def _flush_user(self, app_user_id: str) -> None:
      tweets = self._buffers.pop(app_user_id, [])
      if not tweets or self._enqueue_cb is None:
          return
      priority = self._priorities.pop(app_user_id, NotificationPriority.NORMAL)
      telegram_id = self._telegram_ids.pop(app_user_id, "")
      if not telegram_id:
          return
      payload = NotificationJobPayload(
          app_user_id=app_user_id,
          telegram_id=telegram_id,
          priority=priority,
          tweets=tweets[: self._settings.NOTIFICATIONS_BATCH_MAX_SIZE],
      )
      await self._enqueue_cb(payload)
      logger.info(
          "notification_batch_flushed",
          extra={"app_user_id": app_user_id, "tweet_count": len(payload.tweets)},
      )

  async def flush_all(self) -> None:
      async with self._lock:
          for user_id in list(self._buffers.keys()):
              await self._flush_user(user_id)


def _priority_rank(p: NotificationPriority) -> int:
    if p == NotificationPriority.HIGH:
        return 3
    if p == NotificationPriority.NORMAL:
        return 2
    return 1
