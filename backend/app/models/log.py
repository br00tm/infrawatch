"""Log model for MongoDB."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Log(BaseModel):
    """Log entry model."""

    id: Optional[str] = Field(default=None, alias="_id")
    message: str
    level: LogLevel = LogLevel.INFO
    source: str = Field(..., description="Source of the log (e.g., container name)")
    namespace: Optional[str] = Field(default="default")
    cluster: Optional[str] = Field(default="default")
    pod_name: Optional[str] = None
    container_name: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    def from_mongo(cls, data: dict) -> "Log":
        """Create from MongoDB document."""
        if data is None:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
