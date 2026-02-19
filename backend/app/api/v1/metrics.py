"""Metrics endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_db
from app.models.metric import MetricType
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.metric import (
    MetricAggregation,
    MetricBatchCreate,
    MetricCreate,
    MetricQuery,
    MetricResponse,
)
from app.services.metric_service import MetricService

router = APIRouter()


def get_metric_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> MetricService:
    return MetricService(db)


@router.post("", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
async def create_metric(
    data: MetricCreate,
    service: MetricService = Depends(get_metric_service),
):
    """Create a new metric."""
    metric = await service.create_metric(data)
    return MetricResponse.model_validate(metric.model_dump(by_alias=True))


@router.post("/batch", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_metrics_batch(
    data: MetricBatchCreate,
    service: MetricService = Depends(get_metric_service),
):
    """Create multiple metrics at once."""
    count = await service.create_batch(data.metrics)
    return MessageResponse(message=f"Created {count} metrics")


@router.get("", response_model=PaginatedResponse[MetricResponse])
async def list_metrics(
    metric_type: Optional[MetricType] = None,
    source: Optional[str] = None,
    namespace: Optional[str] = None,
    cluster: Optional[str] = None,
    name: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: MetricService = Depends(get_metric_service),
):
    """List metrics with filters."""
    query = MetricQuery(
        metric_type=metric_type,
        source=source,
        namespace=namespace,
        cluster=cluster,
        name=name,
    )
    return await service.query_metrics(query, page, page_size)


@router.get("/aggregations", response_model=List[MetricAggregation])
async def get_aggregations(
    metric_type: Optional[MetricType] = None,
    source: Optional[str] = None,
    namespace: Optional[str] = None,
    cluster: Optional[str] = None,
    service: MetricService = Depends(get_metric_service),
):
    """Get metric aggregations."""
    query = MetricQuery(
        metric_type=metric_type,
        source=source,
        namespace=namespace,
        cluster=cluster,
    )
    return await service.get_aggregations(query)


@router.get("/source/{source}")
async def get_metrics_by_source(
    source: str,
    limit: int = Query(default=10, ge=1, le=100),
    service: MetricService = Depends(get_metric_service),
):
    """Get latest metrics for a source."""
    metrics = await service.get_latest_by_source(source, limit)
    return [MetricResponse.model_validate(m.model_dump(by_alias=True)) for m in metrics]


@router.get("/{metric_id}", response_model=MetricResponse)
async def get_metric(
    metric_id: str,
    service: MetricService = Depends(get_metric_service),
):
    """Get a metric by ID."""
    metric = await service.get_metric(metric_id)
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metric with id '{metric_id}' not found",
        )
    return MetricResponse.model_validate(metric.model_dump(by_alias=True))


@router.delete("/{metric_id}", response_model=MessageResponse)
async def delete_metric(
    metric_id: str,
    service: MetricService = Depends(get_metric_service),
):
    """Delete a metric."""
    deleted = await service.delete_metric(metric_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Metric with id '{metric_id}' not found",
        )
    return MessageResponse(message="Metric deleted successfully")
