from beanie import Link
from pydantic import Field
from pymongo import IndexModel
from app.models.base import TimestampedDocument
from app.models.user import User


class UserSettings(TimestampedDocument):
    owner: Link[User]
    theme: str = "system"
    language: str = "en"
    timezone: str = "UTC"
    notification_preferences: dict[str, bool] = Field(default_factory=dict)
    profile_settings: dict[str, str] = Field(default_factory=dict)
    privacy_settings: dict[str, bool] = Field(default_factory=dict)
    security_settings: dict[str, bool] = Field(default_factory=dict)
    recent_searches: list[str] = Field(default_factory=list)

    class Settings:
        name = "settings"
        indexes = [
            IndexModel("owner.$id", unique=True),
            IndexModel([("is_deleted", 1), ("updated_at", -1)]),
        ]


class Feedback(TimestampedDocument):
    owner: Link[User] | None = None
    email: str | None = None
    message: str
    status: str = "open"
    rating: int | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    class Settings:
        name = "feedback"
        indexes = [
            IndexModel([("status", 1), ("created_at", -1)]),
            IndexModel([("owner.$id", 1), ("created_at", -1)]),
            IndexModel([("is_deleted", 1), ("updated_at", -1)]),
        ]
