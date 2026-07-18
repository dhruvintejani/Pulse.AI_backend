from beanie import Link
from pydantic import Field
from pymongo import IndexModel
from app.models.base import TimestampedDocument
from app.models.user import User


class Notification(TimestampedDocument):
    owner: Link[User]
    title: str
    description: str
    category: str = "system"
    priority: str = "normal"
    notification_type: str = "info"
    unread: bool = True
    action_url: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    class Settings:
        name = "notifications"
        indexes = [
            IndexModel([("owner.$id", 1), ("unread", 1), ("created_at", -1)]),
            IndexModel([("owner.$id", 1), ("category", 1), ("created_at", -1)]),
            IndexModel([("is_deleted", 1), ("created_at", -1)]),
        ]
