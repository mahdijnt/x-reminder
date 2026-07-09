import pytest
from unittest.mock import AsyncMock

from app.core.config import Settings
from app.infrastructure.qdrant.collections import CollectionsManager


@pytest.mark.asyncio
async def test_ensure_collections_creates_missing_tweets_only():
    settings = Settings(QDRANT_VECTOR_SIZE=384)
    client = AsyncMock()
    client.collection_exists = AsyncMock(side_effect=[False, True, True])
    client.create_collection = AsyncMock()
    client.create_payload_index = AsyncMock()

    manager = CollectionsManager(settings)
    await manager.ensure_all(client)

    assert client.create_collection.await_count == 1
    assert client.create_payload_index.await_count == 2


@pytest.mark.asyncio
async def test_ensure_collections_idempotent_when_exist():
    settings = Settings()
    client = AsyncMock()
    client.collection_exists = AsyncMock(return_value=True)

    manager = CollectionsManager(settings)
    await manager.ensure_all(client)

    client.create_collection.assert_not_awaited()
