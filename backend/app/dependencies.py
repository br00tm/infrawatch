"""Dependency injection for FastAPI."""

from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import get_database


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database dependency."""
    db = await get_database()
    yield db
