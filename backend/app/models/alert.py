"""Alert models for MongoDB."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


class NotificationChannel(str, Enum):
    """Notification channels."""

    EMAIL = "email"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SLACK = "slack"
    WEBHOOK = "webhook"


class Alert(BaseModel):
    """Alert model."""

    id: Optional[str] = Field(default=None, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.WARNING
    status: AlertStatus = AlertStatus.ACTIVE
    source: str
    namespace: Optional[str] = Field(default="default")
    cluster: Optional[str] = Field(default="default")
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    rule_id: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        use_enum_values = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

    def to_mongo(self) -> dict:
        """Convert to MongoDB document."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data and data["_id"]:
            data["_id"] = ObjectId(data["_id"])
        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "Alert":
        """Create from MongoDB document."""
        if data is None:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)


class AlertCondition(BaseModel):
    """Alert rule condition."""

    metric_name: str
    operator: str = Field(..., pattern="^(gt|lt|gte|lte|eq|ne)$")
    threshold: float
    duration_seconds: int = Field(default=60, ge=0)


class AlertRule(BaseModel):
    """Alert rule model."""

    id: Optional[str] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    enabled: bool = True
    severity: AlertSeverity = AlertSeverity.WARNING
    conditions: List[AlertCondition] = Field(default_factory=list)
    namespace_filter: Optional[str] = None
    cluster_filter: Optional[str] = None
    labels_filter: Dict[str, str] = Field(default_factory=dict)
    notification_channels: List[NotificationChannel] = Field(default_factory=list)
    cooldown_minutes: int = Field(default=5, ge=1)
    user_id: str
    last_triggered: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        use_enum_values = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

    def to_mongo(self) -> dict:
        """Convert to MongoDB document."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data and data["_id"]:
            data["_id"] = ObjectId(data["_id"])
        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "AlertRule":
        """Create from MongoDB document."""
        if data is None:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
