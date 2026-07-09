"""Redis-backed watch list storage."""

from __future__ import annotations

from app.infrastructure.redis.keys import RedisKeys, get_redis_keys
from app.models.x.watch_list import WatchListEntry, WatchListType
from app.repositories.redis_repository import RedisRepository


class WatchListRepository:
    def __init__(self, repository: RedisRepository, keys: RedisKeys | None = None) -> None:
        self._repository = repository
        self._keys = keys or get_redis_keys()

    def _hash_key(self, app_user_id: str, list_type: WatchListType) -> str:
        return self._keys.x_watch_list(app_user_id, list_type.value)

    async def list_entries(self, app_user_id: str, list_type: WatchListType) -> list[WatchListEntry]:
        raw = await self._repository.hgetall(self._hash_key(app_user_id, list_type))
        entries: list[WatchListEntry] = []
        for value in raw.values():
            entries.append(WatchListEntry.model_validate_json(value))
        return sorted(entries, key=lambda e: e.username.lower())

    async def add_entry(self, app_user_id: str, list_type: WatchListType, entry: WatchListEntry) -> bool:
        return bool(
            await self._repository.hset(
                self._hash_key(app_user_id, list_type),
                entry.x_user_id,
                entry.model_dump_json(),
            )
        )

    async def remove_entry(self, app_user_id: str, list_type: WatchListType, x_user_id: str) -> int:
        return await self._repository.hdel(self._hash_key(app_user_id, list_type), x_user_id)

    async def replace_all(
        self,
        app_user_id: str,
        list_type: WatchListType,
        entries: list[WatchListEntry],
    ) -> bool:
        key = self._hash_key(app_user_id, list_type)
        await self._repository.delete(key)
        for entry in entries:
            await self.add_entry(app_user_id, list_type, entry)
        return True
