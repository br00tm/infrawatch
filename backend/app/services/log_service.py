"""Log service for business logic."""

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.log import Log, LogLevel
from app.repositories.log_repository import LogRepository
from app.schemas.common import PaginatedResponse
from app.schemas.log import LogCreate, LogQuery, LogResponse


class LogService:
    """Service for log operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.log_repo = LogRepository(db)

    async def create_log(self, data: LogCreate) -> Log:
        """Create a new log entry."""
        return await self.log_repo.create_log(
            message=data.message,
            source=data.source,
            level=data.level,
            namespace=data.namespace,
            cluster=data.cluster,
            pod_name=data.pod_name,
            container_name=data.container_name,
            labels=data.labels,
            metadata=data.metadata,
            timestamp=data.timestamp,
        )

    async def create_batch(self, logs: List[LogCreate]) -> int:
        """Create multiple log entries at once."""
        logs_data = [
            {
                "message": log.message,
                "level": log.level.value if isinstance(log.level, LogLevel) else log.level,
                "source": log.source,
                "namespace": log.namespace,
                "cluster": log.cluster,
                "pod_name": log.pod_name,
                "container_name": log.container_name,
                "labels": log.labels,
                "metadata": log.metadata,
                "timestamp": log.timestamp,
            }
            for log in logs
        ]
        return await self.log_repo.create_batch(logs_data)

    async def get_log(self, log_id: str) -> Optional[Log]:
        """Get a log entry by ID."""
        return await self.log_repo.get_by_id(log_id)

    async def query_logs(
        self,
        query: LogQuery,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResponse[LogResponse]:
        """Query logs with pagination."""
        skip = (page - 1) * page_size
        logs = await self.log_repo.query_logs(
            query=query,
            skip=skip,
            limit=page_size,
        )
        total = await self.log_repo.count_query(query)

        return PaginatedResponse.create(
            items=[LogResponse.model_validate(log.model_dump(by_alias=True)) for log in logs],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_latest_by_source(
        self,
        source: str,
        limit: int = 50,
    ) -> List[Log]:
        """Get latest logs for a source."""
        return await self.log_repo.get_latest_by_source(source, limit)

    async def get_stats(
        self,
        query: Optional[LogQuery] = None,
    ) -> Dict[str, Any]:
        """Get log statistics."""
        return await self.log_repo.get_stats(query)

    async def delete_log(self, log_id: str) -> bool:
        """Delete a log entry."""
        return await self.log_repo.delete(log_id)
