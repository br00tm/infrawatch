"""MongoDB connection management."""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_mongodb() -> None:
    """Connect to MongoDB."""
    global _client, _database

    logger.info("Connecting to MongoDB...", url=settings.mongodb_url.split("@")[-1])

    _client = AsyncIOMotorClient(
        settings.mongodb_url,
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000,
    )
    _database = _client[settings.mongodb_db_name]

    # Test connection
    try:
        await _client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error("Failed to connect to MongoDB", error=str(e))
        raise


async def close_mongodb() -> None:
    """Close MongoDB connection."""
    global _client, _database

    if _client:
        logger.info("Closing MongoDB connection...")
        _client.close()
        _client = None
        _database = None


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if _database is None:
        await connect_mongodb()
    return _database


def get_client() -> Optional[AsyncIOMotorClient]:
    """Get MongoDB client instance."""
    return _client
