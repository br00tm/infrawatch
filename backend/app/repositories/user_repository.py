"""User repository for database operations."""

from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "users", User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        doc = await self.collection.find_one({"email": email})
        if doc:
            return User.from_mongo(doc)
        return None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        doc = await self.collection.find_one({"username": username})
        if doc:
            return User.from_mongo(doc)
        return None

    async def create_user(
        self,
        email: str,
        username: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        is_superuser: bool = False,
    ) -> User:
        """Create a new user."""
        now = datetime.now(timezone.utc)
        user_data = {
            "email": email,
            "username": username,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "is_active": True,
            "is_superuser": is_superuser,
            "roles": ["admin"] if is_superuser else ["user"],
            "created_at": now,
            "updated_at": now,
        }
        return await self.create(user_data)

    async def update_password(self, user_id: str, hashed_password: str) -> Optional[User]:
        """Update user password."""
        return await self.update(
            user_id,
            {
                "hashed_password": hashed_password,
                "updated_at": datetime.now(timezone.utc),
            },
        )

    async def set_active(self, user_id: str, is_active: bool) -> Optional[User]:
        """Set user active status."""
        return await self.update(
            user_id,
            {
                "is_active": is_active,
                "updated_at": datetime.now(timezone.utc),
            },
        )

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return await self.exists({"email": email})

    async def username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        return await self.exists({"username": username})
