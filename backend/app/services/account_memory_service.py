"""Account embedding storage for relationship and similarity search."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.core.config import Settings
from app.integrations.embeddings.service import EmbeddingsService
from app.repositories.qdrant_repository import QdrantRepository
from app.schemas.ai import AccountStoreRequest

logger = logging.getLogger(__name__)


class AccountMemoryService:
    def __init__(
        self,
        settings: Settings,
        repository: QdrantRepository,
        embeddings: EmbeddingsService,
    ) -> None:
        self._settings = settings
        self._repository = repository
        self._embeddings = embeddings

    async def store_account(self, account: AccountStoreRequest) -> None:
        if not self._settings.QDRANT_ENABLED:
            logger.debug("account_memory_skipped_disabled", extra={"user_id": account.user_id})
            return

        text = account.bio or account.username or account.user_id
        vector = await self._embeddings.embed_text(text)
        await self._repository.upsert(
            self._settings.QDRANT_COLLECTION_ACCOUNTS,
            point_id=f"account:{account.user_id}",
            vector=vector,
            payload={
                "user_id": account.user_id,
                "username": account.username,
                "bio": account.bio or "",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "record_type": "account",
            },
        )
