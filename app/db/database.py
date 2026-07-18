from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.models import DOCUMENT_MODELS

mongodb_client: AsyncIOMotorClient | None = None
mongodb_database: AsyncIOMotorDatabase | None = None


async def init_db() -> None:
    global mongodb_client, mongodb_database

    if mongodb_client is not None and mongodb_database is not None:
        return

    mongodb_client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        uuidRepresentation="standard",
        serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
    )
    await mongodb_client.admin.command("ping")
    mongodb_database = mongodb_client[settings.MONGODB_DB_NAME]
    await init_beanie(database=mongodb_database, document_models=DOCUMENT_MODELS)
    logger.info("MongoDB connected and Beanie initialized", database=settings.MONGODB_DB_NAME)


async def close_db() -> None:
    global mongodb_client, mongodb_database

    if mongodb_client is not None:
        mongodb_client.close()
        logger.info("MongoDB connection closed")

    mongodb_client = None
    mongodb_database = None


def get_database() -> AsyncIOMotorDatabase:
    if mongodb_database is None:
        raise RuntimeError("MongoDB database is not initialized")
    return mongodb_database


async def ping_database() -> bool:
    if settings.should_skip_database_init:
        return True
    if mongodb_client is None:
        return False
    try:
        await mongodb_client.admin.command("ping")
    except Exception as exc:
        logger.bind(category="database").warning("MongoDB readiness check failed", error=str(exc))
        return False
    return True
