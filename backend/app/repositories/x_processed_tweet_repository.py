"""Redis storage for processed tweets (notification prep)."""

from __future__ import annotations

from datetime import datetime, timezone

from app.infrastructure.redis.keys import RedisKeys, RedisTTL, get_redis_keys
from app.models.x.tweet import ProcessedTweetRecord
from app.infrastructure.redis.serialization import serialize_json
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

    async def try_claim_pending(
        self,
        app_user_id: str,
        tweet_id: str,
        author_id: str,
        *,
        list_type: str | None = None,
        username: str | None = None,
        url: str | None = None,
        tweet_created_at: datetime | None = None,
    ) -> bool:
        record = ProcessedTweetRecord(
            tweet_id=tweet_id,
            author_id=author_id,
            processed_time=datetime.now(timezone.utc),
            notification_status="pending",
            list_type=list_type,
            username=username,
            url=url,
            tweet_created_at=tweet_created_at,
        )
        key = self._keys.x_processed_tweet(app_user_id, tweet_id)
        payload = serialize_json(record.model_dump(mode="json"))
        claimed = await self._repository.set(key, payload, nx=True, ex=RedisTTL.CACHE_LONG * 7)
        if not claimed:
            return False
        member = f"{app_user_id}:{tweet_id}"
        await self._repository.zadd(
            self._keys.notifications_pending_index(),
            {member: datetime.now(timezone.utc).timestamp()},
        )
        return True

    async def touch_pending(
        self,
        app_user_id: str,
        tweet_id: str,
        author_id: str,
        *,
        list_type: str | None = None,
        username: str | None = None,
        url: str | None = None,
        tweet_created_at: datetime | None = None,
    ) -> bool:
        record = ProcessedTweetRecord(
            tweet_id=tweet_id,
            author_id=author_id,
            processed_time=datetime.now(timezone.utc),
            notification_status="pending",
            list_type=list_type,
            username=username,
            url=url,
            tweet_created_at=tweet_created_at,
        )
        ok = await self.mark_processed(app_user_id, record)
        if ok:
            member = f"{app_user_id}:{tweet_id}"
            await self._repository.zadd(
                self._keys.notifications_pending_index(),
                {member: datetime.now(timezone.utc).timestamp()},
            )
        return ok

    async def set_notification_status(self, app_user_id: str, tweet_id: str, status: str) -> bool:
        record = await self.get(app_user_id, tweet_id)
        if record is None:
            return False
        record.notification_status = status  # type: ignore[assignment]
        ok = await self.mark_processed(app_user_id, record)
        if status != "pending":
            member = f"{app_user_id}:{tweet_id}"
            await self._repository.zrem(self._keys.notifications_pending_index(), member)
        return ok

    async def list_pending(self, app_user_id: str, *, limit: int = 50) -> list[dict]:
        members = await self._repository.zrevrange(self._keys.notifications_pending_index(), 0, limit * 5)
        out: list[dict] = []
        for member in members:
            if not member.startswith(f"{app_user_id}:"):
                continue
            tweet_id = member.split(":", 1)[1]
            record = await self.get(app_user_id, tweet_id)
            if record is None or record.notification_status != "pending":
                await self._repository.zrem(self._keys.notifications_pending_index(), member)
                continue
            out.append({"record": record, "meta": {"list_type": record.list_type or "following"}})
            if len(out) >= limit:
                break
        return out

