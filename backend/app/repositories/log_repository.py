"""Log repository for database operations."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from app.models.log import Log, LogLevel
from app.repositories.base_repository import BaseRepository
from app.schemas.log import LogQuery


class LogRepository(BaseRepository[Log]):
    """Repository for log operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "logs", Log)

    async def create_log(
        self,
        message: str,
        source: str,
        level: LogLevel = LogLevel.INFO,
        namespace: str = "default",
        cluster: str = "default",
        pod_name: Optional[str] = None,
        container_name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> Log:
        """Create a new log entry."""
        log_data = {
            "message": message,
            "level": level.value if isinstance(level, LogLevel) else level,
            "source": source,
            "namespace": namespace,
            "cluster": cluster,
            "pod_name": pod_name,
            "container_name": container_name,
            "labels": labels or {},
            "metadata": metadata or {},
            "timestamp": timestamp or datetime.now(timezone.utc),
        }
        return await self.create(log_data)

    async def create_batch(self, logs: List[Dict[str, Any]]) -> int:
        """Create multiple log entries at once."""
        if not logs:
            return 0
        for log in logs:
            if "timestamp" not in log or log["timestamp"] is None:
                log["timestamp"] = datetime.now(timezone.utc)
        result = await self.collection.insert_many(logs)
        return len(result.inserted_ids)

    async def query_logs(
        self,
        query: LogQuery,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Log]:
        """Query logs with filters."""
        filter_dict = self._build_filter(query)
        return await self.get_all(
            filter=filter_dict,
            skip=skip,
            limit=limit,
            sort=[("timestamp", DESCENDING)],
        )

    async def count_query(self, query: LogQuery) -> int:
        """Count logs matching query."""
        filter_dict = self._build_filter(query)
        return await self.count(filter_dict)

    def _build_filter(self, query: LogQuery) -> Dict[str, Any]:
        """Build MongoDB filter from query."""
        filter_dict: Dict[str, Any] = {}

        if query.level:
            filter_dict["level"] = query.level.value
        if query.source:
            filter_dict["source"] = query.source
        if query.namespace:
            filter_dict["namespace"] = query.namespace
        if query.cluster:
            filter_dict["cluster"] = query.cluster
        if query.pod_name:
            filter_dict["pod_name"] = query.pod_name
        if query.container_name:
            filter_dict["container_name"] = query.container_name

        if query.search:
            filter_dict["$text"] = {"$search": query.search}

        if query.start_time or query.end_time:
            filter_dict["timestamp"] = {}
            if query.start_time:
                filter_dict["timestamp"]["$gte"] = query.start_time
            if query.end_time:
                filter_dict["timestamp"]["$lte"] = query.end_time

        return filter_dict

    async def get_latest_by_source(
        self,
        source: str,
        limit: int = 50,
    ) -> List[Log]:
        """Get latest logs for a source."""
        return await self.get_all(
            filter={"source": source},
            limit=limit,
            sort=[("timestamp", DESCENDING)],
        )

    async def get_stats(
        self,
        query: Optional[LogQuery] = None,
    ) -> Dict[str, Any]:
        """Get log statistics."""
        filter_dict = self._build_filter(query) if query else {}

        pipeline = [
            {"$match": filter_dict},
            {
                "$facet": {
                    "total": [{"$count": "count"}],
                    "by_level": [
                        {"$group": {"_id": "$level", "count": {"$sum": 1}}},
                    ],
                    "by_source": [
                        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 10},
                    ],
                    "by_namespace": [
                        {"$group": {"_id": "$namespace", "count": {"$sum": 1}}},
                    ],
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)

        if not result:
            return {
                "total_count": 0,
                "by_level": {},
                "by_source": {},
                "by_namespace": {},
            }

        data = result[0]
        return {
            "total_count": data["total"][0]["count"] if data["total"] else 0,
            "by_level": {item["_id"]: item["count"] for item in data["by_level"]},
            "by_source": {item["_id"]: item["count"] for item in data["by_source"]},
            "by_namespace": {item["_id"]: item["count"] for item in data["by_namespace"]},
        }
