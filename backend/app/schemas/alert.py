"""Alert schemas for API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.alert import (
    AlertCondition,
    AlertSeverity,
    AlertStatus,
    NotificationChannel,
)


class AlertBase(BaseModel):
    """Base alert schema."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.WARNING
    source: str
    namespace: Optional[str] = "default"
    cluster: Optional[str] = "default"
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AlertCreate(AlertBase):
    """Schema for creating an alert."""

    rule_id: Optional[str] = None


class AlertUpdate(BaseModel):
    """Schema for updating an alert."""

    status: Optional[AlertStatus] = None
    description: Optional[str] = None
    severity: Optional[AlertSeverity] = None


class AlertResponse(AlertBase):
    """Schema for alert response."""

    id: str = Field(..., alias="_id")
    status: AlertStatus
    rule_id: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        populate_by_name = True


class AlertAcknowledge(BaseModel):
    """Schema for acknowledging an alert."""

    comment: Optional[str] = None


class AlertResolve(BaseModel):
    """Schema for resolving an alert."""

    comment: Optional[str] = None


# Alert Rule schemas
class AlertRuleBase(BaseModel):
    """Base alert rule schema."""

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


class AlertRuleCreate(AlertRuleBase):
    """Schema for creating an alert rule."""

    pass


class AlertRuleUpdate(BaseModel):
    """Schema for updating an alert rule."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    severity: Optional[AlertSeverity] = None
    conditions: Optional[List[AlertCondition]] = None
    namespace_filter: Optional[str] = None
    cluster_filter: Optional[str] = None
    labels_filter: Optional[Dict[str, str]] = None
    notification_channels: Optional[List[NotificationChannel]] = None
    cooldown_minutes: Optional[int] = Field(default=None, ge=1)


class AlertRuleResponse(AlertRuleBase):
    """Schema for alert rule response."""

    id: str = Field(..., alias="_id")
    user_id: str
    last_triggered: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class AlertStats(BaseModel):
    """Schema for alert statistics."""

    total_active: int
    total_acknowledged: int
    total_resolved: int
    by_severity: Dict[str, int]
    by_source: Dict[str, int]
