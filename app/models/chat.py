from datetime import datetime
from beanie import Link, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel
from app.models.base import SearchableMixin, TimestampedDocument
from app.models.user import User


class Chat(SearchableMixin, TimestampedDocument):
    owner: Link[User]
    title: str = "New conversation"
    pinned: bool = False
    favorite: bool = False
    model: str | None = None
    provider: str | None = None
    last_message_at: datetime | None = None
    search_text: str = ""

    class Settings:
        name = "chats"
        indexes = [
            IndexModel([("owner.$id", 1), ("updated_at", -1)]),
            IndexModel([("owner.$id", 1), ("pinned", 1), ("updated_at", -1)]),
            IndexModel([("owner.$id", 1), ("favorite", 1), ("updated_at", -1)]),
            IndexModel([("is_deleted", 1), ("updated_at", -1)]),
            IndexModel("search_text"),
        ]


class Message(SearchableMixin, TimestampedDocument):
    owner: Link[User]
    chat_id: PydanticObjectId
    role: str
    content: str
    provider: str | None = None
    model: str | None = None
    reaction: str | None = None
    attachments: list[dict[str, str]] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    search_text: str = ""

    class Settings:
        name = "messages"
        indexes = [
            IndexModel([("owner.$id", 1), ("chat_id", 1), ("created_at", 1)]),
            IndexModel([("chat_id", 1), ("created_at", 1)]),
            IndexModel([("is_deleted", 1), ("updated_at", -1)]),
            IndexModel("search_text"),
        ]
