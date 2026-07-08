"""Domain model placeholders (persistence-ready stubs)."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TimestampedModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class User(TimestampedModel):
    """Placeholder user aggregate."""

    email: str | None = None
    display_name: str | None = None
    is_active: bool = True
