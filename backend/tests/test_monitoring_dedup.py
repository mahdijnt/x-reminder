"""Monitoring dedup and cursor store smoke tests."""

from __future__ import annotations

import asyncio
import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.monitoring.last_poll_store import LastPollStore, max_tweet_id
from app.models.x.tweet import ProcessedTweetRecord
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository


class _MemoryRedis:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._data.get(key)

    async def set(self, key: str, value: str, *, ex=None, px=None, nx=False, xx=False) -> bool:
        if nx and key in self._data:
            return False
        if xx and key not in self._data:
            return False
        self._data[key] = value
        return True

    async def exists(self, *keys: str) -> int:
        return sum(1 for k in keys if k in self._data)

    async def zadd(self, key: str, mapping: dict[str, float]) -> bool:
        return True

    async def zrem(self, key: str, member: str) -> int:
        return 0


class _RepoWrapper:
    def __init__(self, memory: _MemoryRedis) -> None:
        self._memory = memory

    async def get(self, key: str):
        return await self._memory.get(key)

    async def set(self, key: str, value: str, *, ex=None, px=None, nx=False, xx=False) -> bool:
        return await self._memory.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    async def exists(self, *keys: str) -> int:
        return await self._memory.exists(*keys)

    async def zadd(self, key: str, mapping: dict[str, float]) -> bool:
        return await self._memory.zadd(key, mapping)

    async def zrem(self, key: str, member: str) -> int:
        return await self._memory.zrem(key, member)


class MonitoringDedupTests(unittest.IsolatedAsyncioTestCase):
    async def test_try_claim_pending_is_idempotent(self) -> None:
        memory = _MemoryRedis()
        repo = ProcessedTweetRepository(_RepoWrapper(memory))
        ok1 = await repo.try_claim_pending("user1", "100", "author1", list_type="following")
        ok2 = await repo.try_claim_pending("user1", "100", "author1", list_type="following")
        self.assertTrue(ok1)
        self.assertFalse(ok2)
        self.assertTrue(await repo.is_processed("user1", "100"))

    async def test_last_processed_tweet_id_monotonic(self) -> None:
        memory = _MemoryRedis()
        store = LastPollStore(_RepoWrapper(memory))
        await store.set_last_processed_tweet_id("u", "following", "x1", "50")
        await store.set_last_processed_tweet_id("u", "following", "x1", "40")
        self.assertEqual(await store.get_last_processed_tweet_id("u", "following", "x1"), "50")
        await store.set_last_processed_tweet_id("u", "following", "x1", "99")
        self.assertEqual(await store.get_last_processed_tweet_id("u", "following", "x1"), "99")

    def test_max_tweet_id_numeric(self) -> None:
        self.assertEqual(max_tweet_id("10", "20"), "20")
        self.assertEqual(max_tweet_id("20", "9"), "20")


if __name__ == "__main__":
    unittest.main()
