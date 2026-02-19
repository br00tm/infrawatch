"""Metric service for business logic."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.metric import Metric, MetricType
from app.repositories.metric_repository import MetricRepository
from app.schemas.common import PaginatedResponse
from app.schemas.metric import MetricCreate, MetricQuery, MetricResponse


class MetricService:
    """Service for metric operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.metric_repo = MetricRepository(db)

    async def create_metric(self, data: MetricCreate) -> Metric:
        """Create a new metric."""
        return await self.metric_repo.create_metric(
            name=data.name,
            value=data.value,
            source=data.source,
            metric_type=data.metric_type,
            unit=data.unit,
            namespace=data.namespace,
            cluster=data.cluster,
            labels=data.labels,
            metadata=data.metadata,
            timestamp=data.timestamp,
        )

    async def create_batch(self, metrics: List[MetricCreate]) -> int:
        """Create multiple metrics at once."""
        metrics_data = [
            {
                "name": m.name,
                "metric_type": m.metric_type.value if isinstance(m.metric_type, MetricType) else m.metric_type,
                "value": m.value,
                "unit": m.unit,
                "source": m.source,
                "namespace": m.namespace,
                "cluster": m.cluster,
                "labels": m.labels,
                "metadata": m.metadata,
                "timestamp": m.timestamp,
            }
            for m in metrics
        ]
        return await self.metric_repo.create_batch(metrics_data)

    async def get_metric(self, metric_id: str) -> Optional[Metric]:
        """Get a metric by ID."""
        return await self.metric_repo.get_by_id(metric_id)

    async def query_metrics(
        self,
        query: MetricQuery,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[MetricResponse]:
        """Query metrics with pagination."""
        skip = (page - 1) * page_size
        metrics = await self.metric_repo.query_metrics(
            query=query,
            skip=skip,
            limit=page_size,
        )
        total = await self.metric_repo.count_query(query)

        return PaginatedResponse.create(
            items=[MetricResponse.model_validate(m.model_dump(by_alias=True)) for m in metrics],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_latest_by_source(
        self,
        source: str,
        limit: int = 10,
    ) -> List[Metric]:
        """Get latest metrics for a source."""
        return await self.metric_repo.get_latest_by_source(source, limit)

    async def get_aggregations(
        self,
        query: MetricQuery,
    ) -> List[Dict[str, Any]]:
        """Get metric aggregations."""
        return await self.metric_repo.get_aggregations(query)

    async def delete_metric(self, metric_id: str) -> bool:
        """Delete a metric."""
        return await self.metric_repo.delete(metric_id)
