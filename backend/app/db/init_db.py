"""Database initialization utilities."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logging import get_logger
from app.core.security import get_password_hash
from app.db.indexes import create_indexes

logger = get_logger(__name__)


async def init_database(db: AsyncIOMotorDatabase) -> None:
    """Initialize the database with indexes and default data."""
    logger.info("Initializing database...")

    # Create indexes
    await create_indexes(db)

    # Create default admin user if not exists
    await create_default_admin(db)

    logger.info("Database initialization completed")


async def create_default_admin(db: AsyncIOMotorDatabase) -> None:
    """Create default admin user if not exists."""
    admin_email = "admin@infrawatch.dev"

    existing_admin = await db.users.find_one({"email": admin_email})
    if existing_admin:
        logger.info("Default admin user already exists")
        return

    admin_user = {
        "email": admin_email,
        "username": "admin",
        "hashed_password": get_password_hash("admin123"),
        "full_name": "System Administrator",
        "is_active": True,
        "is_superuser": True,
        "roles": ["admin"],
        "created_at": None,  # Will be set by the model
        "updated_at": None,
    }

    from datetime import datetime, timezone

    admin_user["created_at"] = datetime.now(timezone.utc)
    admin_user["updated_at"] = datetime.now(timezone.utc)

    await db.users.insert_one(admin_user)
    logger.info("Default admin user created", email=admin_email)
