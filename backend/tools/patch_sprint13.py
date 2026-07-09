from pathlib import Path
ROOT = Path(r"E:\GitHub\x-reminder\backend")

keys = (ROOT / "app/infrastructure/redis/keys.py").read_text(encoding="utf-8")
if "notifications_queue" not in keys:
    block = """
    def notifications_queue(self) -> str:
        return self._key(\"notifications\", \"queue\")

    def notifications_queue_priority(self, level: str) -> str:
        return self._key(\"notifications\", \"queue\", \"priority\", level)

    def notifications_retry(self) -> str:
        return self._key(\"notifications\", \"retry\")

    def notifications_failures(self) -> str:
        return self._key(\"notifications\", \"failures\")

    def notifications_failure_item(self, failure_id: str) -> str:
        return self._key(\"notifications\", \"failures\", \"item\", failure_id)

    def notifications_history(self, notification_id: str) -> str:
        return self._key(\"notifications\", \"history\", notification_id)

    def notifications_history_index(self) -> str:
        return self._key(\"notifications\", \"history\", \"index\")

    def notifications_metrics(self) -> str:
        return self._key(\"notifications\", \"metrics\")

    def notifications_dedup(self, user_id: str, tweet_id: str) -> str:
        return self._key(\"notifications\", \"dedup\", user_id, tweet_id)

    def notifications_pending_index(self) -> str:
        return self._key(\"notifications\", \"pending\")

"""
    keys = keys.replace("\ndef get_redis_keys", block + "\n\ndef get_redis_keys")
    (ROOT / "app/infrastructure/redis/keys.py").write_text(keys, encoding="utf-8")
    print("patched keys")

tweet = (ROOT / "app/models/x/tweet.py").read_text(encoding="utf-8")
if "list_type" not in tweet:
    tweet = tweet.replace(
        "Literal[\"pending\", \"sent\", \"skipped\"]",
        "Literal[\"pending\", \"sent\", \"skipped\", \"failed\"]",
    )
    tweet = tweet.replace(
        "    notification_status: Literal[\"pending\", \"sent\", \"skipped\", \"failed\"] = \"pending\"",
        "    notification_status: Literal[\"pending\", \"sent\", \"skipped\", \"failed\"] = \"pending\"\n"
        "    list_type: str | None = None\n"
        "    username: str | None = None\n"
        "    url: str | None = None\n"
        "    tweet_created_at: datetime | None = None",
    )
    (ROOT / "app/models/x/tweet.py").write_text(tweet, encoding="utf-8")
    print("patched tweet model")

repo_path = ROOT / "app/repositories/x_processed_tweet_repository.py"
repo = repo_path.read_text(encoding="utf-8")
if "list_pending" not in repo:
    repo = repo.replace(
        "    async def touch_pending(self, app_user_id: str, tweet_id: str, author_id: str) -> bool:",
        "    async def touch_pending(\n"
        "        self,\n"
        "        app_user_id: str,\n"
        "        tweet_id: str,\n"
        "        author_id: str,\n"
        "        *,\n"
        "        list_type: str | None = None,\n"
        "        username: str | None = None,\n"
        "        url: str | None = None,\n"
        "        tweet_created_at: datetime | None = None,\n"
        "    ) -> bool:",
    )
    old_record = """        record = ProcessedTweetRecord(
            tweet_id=tweet_id,
            author_id=author_id,
            processed_time=datetime.now(timezone.utc),
            notification_status=\"pending\",
        )
        return await self.mark_processed(app_user_id, record)"""
    new_record = """        record = ProcessedTweetRecord(
            tweet_id=tweet_id,
            author_id=author_id,
            processed_time=datetime.now(timezone.utc),
            notification_status=\"pending\",
            list_type=list_type,
            username=username,
            url=url,
            tweet_created_at=tweet_created_at,
        )
        ok = await self.mark_processed(app_user_id, record)
        if ok:
            member = f\"{app_user_id}:{tweet_id}\"
            await self._repository.zadd(
                self._keys.notifications_pending_index(),
                {member: datetime.now(timezone.utc).timestamp()},
            )
        return ok"""
    repo = repo.replace(old_record, new_record)
    repo = repo.rstrip() + """

    async def set_notification_status(self, app_user_id: str, tweet_id: str, status: str) -> bool:
        record = await self.get(app_user_id, tweet_id)
        if record is None:
            return False
        record.notification_status = status  # type: ignore[assignment]
        ok = await self.mark_processed(app_user_id, record)
        if status != \"pending\":
            member = f\"{app_user_id}:{tweet_id}\"
            await self._repository.zrem(self._keys.notifications_pending_index(), member)
        return ok

    async def list_pending(self, app_user_id: str, *, limit: int = 50) -> list[dict]:
        members = await self._repository.zrevrange(self._keys.notifications_pending_index(), 0, limit * 5)
        out: list[dict] = []
        for member in members:
            if not member.startswith(f\"{app_user_id}:\"):
                continue
            tweet_id = member.split(\":\", 1)[1]
            record = await self.get(app_user_id, tweet_id)
            if record is None or record.notification_status != \"pending\":
                await self._repository.zrem(self._keys.notifications_pending_index(), member)
                continue
            out.append({\"record\": record, \"meta\": {\"list_type\": record.list_type or \"following\"}})
            if len(out) >= limit:
                break
        return out
"""
    repo_path.write_text(repo + "\n", encoding="utf-8")
    print("patched processed repo")

router = (ROOT / "app/api/v1/router.py").read_text(encoding="utf-8")
if "notifications" not in router:
    router = router.replace(
        "from app.api.v1.endpoints import auth_x, health, monitoring, watch_lists, x_profile",
        "from app.api.v1.endpoints import auth_x, health, monitoring, notifications, watch_lists, x_profile",
    )
    router = router.replace(
        "api_router.include_router(monitoring.router)",
        "api_router.include_router(monitoring.router)\napi_router.include_router(notifications.router)",
    )
    (ROOT / "app/api/v1/router.py").write_text(router, encoding="utf-8")
    print("patched router")