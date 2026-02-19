"""Pydantic schemas for API request/response validation."""

from app.schemas.alert import (
    AlertCreate,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
    AlertUpdate,
)
from app.schemas.common import (
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.schemas.log import LogCreate, LogQuery, LogResponse
from app.schemas.metric import MetricCreate, MetricQuery, MetricResponse
from app.schemas.user import (
    Token,
    TokenPayload,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenPayload",
    # Metric
    "MetricCreate",
    "MetricResponse",
    "MetricQuery",
    # Log
    "LogCreate",
    "LogResponse",
    "LogQuery",
    # Alert
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "AlertRuleCreate",
    "AlertRuleUpdate",
    "AlertRuleResponse",
    # Common
    "PaginationParams",
    "PaginatedResponse",
    "MessageResponse",
]
