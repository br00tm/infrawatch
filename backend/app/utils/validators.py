"""Validation utilities."""

from bson import ObjectId


def validate_object_id(id_str: str) -> bool:
    """Validate if string is a valid MongoDB ObjectId."""
    return ObjectId.is_valid(id_str)


def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username (alphanumeric, underscores, 3-50 chars)."""
    import re
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return bool(re.match(pattern, username))
