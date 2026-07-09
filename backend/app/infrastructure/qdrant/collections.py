"""Ensure Qdrant collections exist on startup."""

from __future__ import annotations

import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import Settings

logger = logging.getLogger(__name__)


class CollectionsManager:
    """Create or verify vector collections."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def ensure_all(self, client: AsyncQdrantClient) -> None:
        await self._ensure_tweets(client)
        await self._ensure_accounts(client)
        await self._ensure_conversations(client)

    async def _ensure_collection(
        self,
        client: AsyncQdrantClient,
        name: str,
        *,
        vector_size: int,
    ) -> bool:
        exists = await client.collection_exists(name)
        if exists:
            logger.info("qdrant_collection_exists", extra={"collection": name})
            return False

        await client.create_collection(
            collection_name=name,
            vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
        )
        logger.info("qdrant_collection_created", extra={"collection": name})
        return True

    async def _ensure_tweets(self, client: AsyncQdrantClient) -> None:
        name = self._settings.QDRANT_COLLECTION_TWEETS
        created = await self._ensure_collection(client, name, vector_size=self._settings.QDRANT_VECTOR_SIZE)
        if created:
            await client.create_payload_index(
                collection_name=name,
                field_name="tweet_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD,
            )
            await client.create_payload_index(
                collection_name=name,
                field_name="user_id",
                field_schema=qmodels.PayloadSchemaType.KEYWORD,
            )

    async def _ensure_accounts(self, client: AsyncQdrantClient) -> None:
        name = self._settings.QDRANT_COLLECTION_ACCOUNTS
        created = await self._ensure_collection(client, name, vector_size=self._settings.QDRANT_VECTOR_SIZE)
        if not created:
            return
        await client.create_payload_index(
            collection_name=name,
            field_name="user_id",
            field_schema=qmodels.PayloadSchemaType.KEYWORD,
        )
        await client.create_payload_index(
            collection_name=name,
            field_name="username",
            field_schema=qmodels.PayloadSchemaType.KEYWORD,
        )

    async def _ensure_conversations(self, client: AsyncQdrantClient) -> None:
        name = self._settings.QDRANT_COLLECTION_CONVERSATIONS
        created = await self._ensure_collection(client, name, vector_size=self._settings.QDRANT_VECTOR_SIZE)
        if not created:
            return
        await client.create_payload_index(
            collection_name=name,
            field_name="session_id",
            field_schema=qmodels.PayloadSchemaType.KEYWORD,
        )