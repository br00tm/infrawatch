"""Authentication service."""

from typing import Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import AuthenticationError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, UserCreate


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if email exists
        if await self.user_repo.email_exists(user_data.email):
            raise ValidationError("Email already registered")

        # Check if username exists
        if await self.user_repo.username_exists(user_data.username):
            raise ValidationError("Username already taken")

        # Hash password and create user
        hashed_password = get_password_hash(user_data.password)
        user = await self.user_repo.create_user(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )
        return user

    async def authenticate(self, email: str, password: str) -> Tuple[User, Token]:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        tokens = self._generate_tokens(user)
        return user, tokens

    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token."""
        payload = verify_token(refresh_token, token_type="refresh")

        if not payload:
            raise AuthenticationError("Invalid refresh token")

        user = await self.user_repo.get_by_id(payload["sub"])

        if not user:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        return self._generate_tokens(user)

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        payload = verify_token(token, token_type="access")

        if not payload:
            return None

        user = await self.user_repo.get_by_id(payload["sub"])
        return user

    def _generate_tokens(self, user: User) -> Token:
        """Generate access and refresh tokens for user."""
        token_data = {
            "sub": user.id,
            "email": user.email,
            "roles": user.roles,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )
