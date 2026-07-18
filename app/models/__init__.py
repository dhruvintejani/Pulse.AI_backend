from app.models.chat import Chat, Message
from app.models.document import DocumentFile, Folder
from app.models.notification import Notification
from app.models.settings import Feedback, UserSettings
from app.models.user import User

DOCUMENT_MODELS = [User, Chat, Message, Folder, DocumentFile, Notification, UserSettings, Feedback]

__all__ = [
    "Chat",
    "DOCUMENT_MODELS",
    "DocumentFile",
    "Feedback",
    "Folder",
    "Message",
    "Notification",
    "User",
    "UserSettings",
]
