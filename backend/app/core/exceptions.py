"""Custom exceptions for the application."""

from typing import Any, Dict, Optional


class InfraWatchException(Exception):
    """Base exception for InfraWatch application."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(InfraWatchException):
    """Resource not found exception."""

    def __init__(
        self,
        resource: str,
        resource_id: Optional[str] = None,
    ):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=message, status_code=404)


class ValidationError(InfraWatchException):
    """Validation error exception."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=422, details=details)


class AuthenticationError(InfraWatchException):
    """Authentication error exception."""

    def __init__(
        self,
        message: str = "Could not validate credentials",
    ):
        super().__init__(message=message, status_code=401)


class AuthorizationError(InfraWatchException):
    """Authorization error exception."""

    def __init__(
        self,
        message: str = "Not authorized to perform this action",
    ):
        super().__init__(message=message, status_code=403)


class DatabaseError(InfraWatchException):
    """Database operation error."""

    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=500, details=details)


class ExternalServiceError(InfraWatchException):
    """External service error."""

    def __init__(
        self,
        service: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        full_message = f"External service '{service}' error: {message}"
        super().__init__(message=full_message, status_code=502, details=details)
