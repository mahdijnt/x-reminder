"""Abstract repository and in-memory stub implementation."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base contract for data access implementations."""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[T]:
        raise NotImplementedError


class InMemoryRepository(BaseRepository[dict[str, str]]):
    """Simple in-memory store for development and tests."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, str]] = {}

    async def get_by_id(self, entity_id: str) -> dict[str, str] | None:
        return self._store.get(entity_id)

    async def list_all(self) -> list[dict[str, str]]:
        return list(self._store.values())
