from beanie import Indexed
from pydantic import EmailStr, Field
from pymongo import IndexModel
from app.models.base import SearchableMixin, TimestampedDocument


class User(SearchableMixin, TimestampedDocument):
    clerk_user_id: Indexed(str, unique=True)
    email: Indexed(EmailStr)
    name: str
    image_url: str | None = None
    role: str = "member"
    is_admin: bool = False
    is_active: bool = True
    search_text: str = ""
    metadata: dict[str, str] = Field(default_factory=dict)

    class Settings:
        name = "users"
        indexes = [
            IndexModel("email"),
            IndexModel("clerk_user_id", unique=True),
            IndexModel([("is_deleted", 1), ("updated_at", -1)]),
            IndexModel("search_text"),
        ]
