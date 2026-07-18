from beanie import Link, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel
from app.models.base import SearchableMixin, TimestampedDocument
from app.models.user import User


class Folder(SearchableMixin, TimestampedDocument):
    owner: Link[User]
    name: str
    parent_id: PydanticObjectId | None = None
    search_text: str = ""

    class Settings:
        name = "folders"
        indexes = [
            IndexModel([("owner.$id", 1), ("parent_id", 1), ("name", 1)]),
            IndexModel([("is_deleted", 1), ("updated_at", -1)]),
            IndexModel("search_text"),
        ]


class DocumentFile(SearchableMixin, TimestampedDocument):
    owner: Link[User]
    folder_id: PydanticObjectId | None = None
    name: str
    file_type: str
    mime_type: str | None = None
    size_bytes: int = 0
    category: str = "General"
    tags: list[str] = Field(default_factory=list)
    storage_provider: str = "metadata"
    storage_public_id: str | None = None
    preview_text: str | None = None
    search_text: str = ""

    class Settings:
        name = "documents"
        indexes = [
            IndexModel([("owner.$id", 1), ("updated_at", -1)]),
            IndexModel([("owner.$id", 1), ("folder_id", 1), ("updated_at", -1)]),
            IndexModel([("owner.$id", 1), ("category", 1)]),
            IndexModel([("owner.$id", 1), ("tags", 1)]),
            IndexModel([("is_deleted", 1), ("updated_at", -1)]),
            IndexModel("search_text"),
        ]
