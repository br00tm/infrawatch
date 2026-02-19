"""Logs endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_db
from app.models.log import LogLevel
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.log import LogBatchCreate, LogCreate, LogQuery, LogResponse, LogStats
from app.services.log_service import LogService

router = APIRouter()


def get_log_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> LogService:
    return LogService(db)


@router.post("", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    data: LogCreate,
    service: LogService = Depends(get_log_service),
):
    """Create a new log entry."""
    log = await service.create_log(data)
    return LogResponse.model_validate(log.model_dump(by_alias=True))


@router.post("/batch", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_logs_batch(
    data: LogBatchCreate,
    service: LogService = Depends(get_log_service),
):
    """Create multiple log entries at once."""
    count = await service.create_batch(data.logs)
    return MessageResponse(message=f"Created {count} log entries")


@router.get("", response_model=PaginatedResponse[LogResponse])
async def list_logs(
    level: Optional[LogLevel] = None,
    source: Optional[str] = None,
    namespace: Optional[str] = None,
    cluster: Optional[str] = None,
    pod_name: Optional[str] = None,
    container_name: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: LogService = Depends(get_log_service),
):
    """List logs with filters."""
    query = LogQuery(
        level=level,
        source=source,
        namespace=namespace,
        cluster=cluster,
        pod_name=pod_name,
        container_name=container_name,
        search=search,
    )
    return await service.query_logs(query, page, page_size)


@router.get("/stats", response_model=LogStats)
async def get_log_stats(
    level: Optional[LogLevel] = None,
    source: Optional[str] = None,
    namespace: Optional[str] = None,
    service: LogService = Depends(get_log_service),
):
    """Get log statistics."""
    query = LogQuery(level=level, source=source, namespace=namespace)
    stats = await service.get_stats(query)
    return LogStats(**stats)


@router.get("/source/{source}")
async def get_logs_by_source(
    source: str,
    limit: int = Query(default=50, ge=1, le=200),
    service: LogService = Depends(get_log_service),
):
    """Get latest logs for a source."""
    logs = await service.get_latest_by_source(source, limit)
    return [LogResponse.model_validate(log.model_dump(by_alias=True)) for log in logs]


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: str,
    service: LogService = Depends(get_log_service),
):
    """Get a log entry by ID."""
    log = await service.get_log(log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log with id '{log_id}' not found",
        )
    return LogResponse.model_validate(log.model_dump(by_alias=True))


@router.delete("/{log_id}", response_model=MessageResponse)
async def delete_log(
    log_id: str,
    service: LogService = Depends(get_log_service),
):
    """Delete a log entry."""
    deleted = await service.delete_log(log_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log with id '{log_id}' not found",
        )
    return MessageResponse(message="Log deleted successfully")
