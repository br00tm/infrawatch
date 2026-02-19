"""Log schemas for API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.log import LogLevel


class LogBase(BaseModel):
    """Base log schema."""

    message: str
    level: LogLevel = LogLevel.INFO
    source: str
    namespace: Optional[str] = "default"
    cluster: Optional[str] = "default"
    pod_name: Optional[str] = None
    container_name: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LogCreate(LogBase):
    """Schema for creating a log entry."""

    timestamp: Optional[datetime] = None


class LogBatchCreate(BaseModel):
    """Schema for creating multiple log entries."""

    logs: List[LogCreate]


class LogResponse(LogBase):
    """Schema for log response."""

    id: str = Field(..., alias="_id")
    timestamp: datetime

    class Config:
        populate_by_name = True


class LogQuery(BaseModel):
    """Schema for querying logs."""

    level: Optional[LogLevel] = None
    source: Optional[str] = None
    namespace: Optional[str] = None
    cluster: Optional[str] = None
    pod_name: Optional[str] = None
    container_name: Optional[str] = None
    search: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class LogStats(BaseModel):
    """Schema for log statistics."""

    total_count: int
    by_level: Dict[str, int]
    by_source: Dict[str, int]
    by_namespace: Dict[str, int]
