"""Metric repository for database operations."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from app.models.metric import Metric, MetricType
from app.repositories.base_repository import BaseRepository
from app.schemas.metric import MetricQuery


class MetricRepository(BaseRepository[Metric]):
    """Repository for metric operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "metrics", Metric)

    async def create_metric(
        self,
        name: str,
        value: float,
        source: str,
        metric_type: MetricType = MetricType.CUSTOM,
        unit: Optional[str] = None,
        namespace: str = "default",
        cluster: str = "default",
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> Metric:
        """Create a new metric."""
        metric_data = {
            "name": name,
            "metric_type": metric_type.value if isinstance(metric_type, MetricType) else metric_type,
            "value": value,
            "unit": unit,
            "source": source,
            "namespace": namespace,
            "cluster": cluster,
            "labels": labels or {},
            "metadata": metadata or {},
            "timestamp": timestamp or datetime.now(timezone.utc),
        }
        return await self.create(metric_data)

    async def create_batch(self, metrics: List[Dict[str, Any]]) -> int:
        """Create multiple metrics at once."""
        if not metrics:
            return 0
        for metric in metrics:
            if "timestamp" not in metric or metric["timestamp"] is None:
                metric["timestamp"] = datetime.now(timezone.utc)
        result = await self.collection.insert_many(metrics)
        return len(result.inserted_ids)

    async def query_metrics(
        self,
        query: MetricQuery,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Metric]:
        """Query metrics with filters."""
        filter_dict = self._build_filter(query)
        return await self.get_all(
            filter=filter_dict,
            skip=skip,
            limit=limit,
            sort=[("timestamp", DESCENDING)],
        )

    async def count_query(self, query: MetricQuery) -> int:
        """Count metrics matching query."""
        filter_dict = self._build_filter(query)
        return await self.count(filter_dict)

    def _build_filter(self, query: MetricQuery) -> Dict[str, Any]:
        """Build MongoDB filter from query."""
        filter_dict: Dict[str, Any] = {}

        if query.metric_type:
            filter_dict["metric_type"] = query.metric_type.value
        if query.source:
            filter_dict["source"] = query.source
        if query.namespace:
            filter_dict["namespace"] = query.namespace
        if query.cluster:
            filter_dict["cluster"] = query.cluster
        if query.name:
            filter_dict["name"] = query.name

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
        limit: int = 10,
    ) -> List[Metric]:
        """Get latest metrics for a source."""
        return await self.get_all(
            filter={"source": source},
            limit=limit,
            sort=[("timestamp", DESCENDING)],
        )

    async def get_aggregations(
        self,
        query: MetricQuery,
    ) -> List[Dict[str, Any]]:
        """Get metric aggregations."""
        filter_dict = self._build_filter(query)

        pipeline = [
            {"$match": filter_dict},
            {
                "$group": {
                    "_id": {
                        "name": "$name",
                        "metric_type": "$metric_type",
                    },
                    "avg_value": {"$avg": "$value"},
                    "min_value": {"$min": "$value"},
                    "max_value": {"$max": "$value"},
                    "count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id.name",
                    "metric_type": "$_id.metric_type",
                    "avg_value": {"$round": ["$avg_value", 2]},
                    "min_value": {"$round": ["$min_value", 2]},
                    "max_value": {"$round": ["$max_value", 2]},
                    "count": 1,
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=100)
