from datetime import UTC, datetime
from typing import Any
from beanie import Document
from pydantic import Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampedDocument(Document):
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    deleted_at: datetime | None = None
    is_deleted: bool = False

    async def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = utc_now()
        self.updated_at = utc_now()
        await self.save()

    def touch(self) -> None:
        self.updated_at = utc_now()

    class Settings:
        use_state_management = True


class SearchableMixin:
    search_text: str = ""

    @staticmethod
    def build_search_text(*values: Any) -> str:
        return " ".join(str(value).lower() for value in values if value is not None)
