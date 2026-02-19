"""Metric schemas for API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.metric import MetricType


class MetricBase(BaseModel):
    """Base metric schema."""

    name: str = Field(..., min_length=1, max_length=100)
    metric_type: MetricType = MetricType.CUSTOM
    value: float
    unit: Optional[str] = None
    source: str
    namespace: Optional[str] = "default"
    cluster: Optional[str] = "default"
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetricCreate(MetricBase):
    """Schema for creating a metric."""

    timestamp: Optional[datetime] = None


class MetricBatchCreate(BaseModel):
    """Schema for creating multiple metrics."""

    metrics: List[MetricCreate]


class MetricResponse(MetricBase):
    """Schema for metric response."""

    id: str = Field(..., alias="_id")
    timestamp: datetime

    class Config:
        populate_by_name = True


class MetricQuery(BaseModel):
    """Schema for querying metrics."""

    metric_type: Optional[MetricType] = None
    source: Optional[str] = None
    namespace: Optional[str] = None
    cluster: Optional[str] = None
    name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class MetricAggregation(BaseModel):
    """Schema for metric aggregation results."""

    name: str
    metric_type: str
    avg_value: float
    min_value: float
    max_value: float
    count: int
    source: Optional[str] = None
    namespace: Optional[str] = None
