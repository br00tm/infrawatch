"""Alerts endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.websocket import manager as ws_manager
from app.core.exceptions import NotFoundError, ValidationError
from app.dependencies import get_db
from app.models.alert import AlertStatus
from app.schemas.alert import (
    AlertAcknowledge,
    AlertCreate,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
    AlertStats,
    AlertUpdate,
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.alert_service import AlertService
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()


def get_alert_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> AlertService:
    return AlertService(db)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> str:
    """Get current user ID from token."""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return user.id


# Alert endpoints
@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    data: AlertCreate,
    service: AlertService = Depends(get_alert_service),
):
    """Create a new alert."""
    alert = await service.create_alert(data)
    response = AlertResponse.model_validate(alert.model_dump(by_alias=True))
    await ws_manager.broadcast("alert", response.model_dump(mode="json"))
    return response


@router.get("", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    status_filter: Optional[AlertStatus] = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: AlertService = Depends(get_alert_service),
):
    """List alerts with optional status filter."""
    result = await service.get_alerts(status_filter, page, page_size)
    return PaginatedResponse.create(
        items=[AlertResponse.model_validate(a.model_dump(by_alias=True)) for a in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get("/stats", response_model=AlertStats)
async def get_alert_stats(
    service: AlertService = Depends(get_alert_service),
):
    """Get alert statistics."""
    stats = await service.get_alert_stats()
    return AlertStats(**stats)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    service: AlertService = Depends(get_alert_service),
):
    """Get an alert by ID."""
    alert = await service.get_alert(alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )
    return AlertResponse.model_validate(alert.model_dump(by_alias=True))


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    data: AlertUpdate,
    service: AlertService = Depends(get_alert_service),
):
    """Update an alert."""
    alert = await service.update_alert(alert_id, data)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )
    return AlertResponse.model_validate(alert.model_dump(by_alias=True))


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: str,
    data: AlertAcknowledge = None,
    user_id: str = Depends(get_current_user_id),
    service: AlertService = Depends(get_alert_service),
):
    """Acknowledge an alert."""
    try:
        alert = await service.acknowledge_alert(alert_id, user_id)
        return AlertResponse.model_validate(alert.model_dump(by_alias=True))
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: str,
    service: AlertService = Depends(get_alert_service),
):
    """Resolve an alert."""
    try:
        alert = await service.resolve_alert(alert_id)
        return AlertResponse.model_validate(alert.model_dump(by_alias=True))
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )


@router.delete("/{alert_id}", response_model=MessageResponse)
async def delete_alert(
    alert_id: str,
    service: AlertService = Depends(get_alert_service),
):
    """Delete an alert."""
    deleted = await service.delete_alert(alert_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id '{alert_id}' not found",
        )
    return MessageResponse(message="Alert deleted successfully")


# Alert Rule endpoints
@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    data: AlertRuleCreate,
    user_id: str = Depends(get_current_user_id),
    service: AlertService = Depends(get_alert_service),
):
    """Create a new alert rule."""
    try:
        rule = await service.create_rule(data, user_id)
        return AlertRuleResponse.model_validate(rule.model_dump(by_alias=True))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/rules", response_model=PaginatedResponse[AlertRuleResponse])
async def list_alert_rules(
    user_id: str = Depends(get_current_user_id),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: AlertService = Depends(get_alert_service),
):
    """List alert rules for current user."""
    result = await service.get_user_rules(user_id, page, page_size)
    return PaginatedResponse.create(
        items=[AlertRuleResponse.model_validate(r.model_dump(by_alias=True)) for r in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: str,
    service: AlertService = Depends(get_alert_service),
):
    """Get an alert rule by ID."""
    rule = await service.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with id '{rule_id}' not found",
        )
    return AlertRuleResponse.model_validate(rule.model_dump(by_alias=True))


@router.patch("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: str,
    data: AlertRuleUpdate,
    service: AlertService = Depends(get_alert_service),
):
    """Update an alert rule."""
    rule = await service.update_rule(rule_id, data)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with id '{rule_id}' not found",
        )
    return AlertRuleResponse.model_validate(rule.model_dump(by_alias=True))


@router.post("/rules/{rule_id}/toggle", response_model=AlertRuleResponse)
async def toggle_alert_rule(
    rule_id: str,
    enabled: bool = Query(...),
    service: AlertService = Depends(get_alert_service),
):
    """Enable or disable an alert rule."""
    rule = await service.toggle_rule(rule_id, enabled)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with id '{rule_id}' not found",
        )
    return AlertRuleResponse.model_validate(rule.model_dump(by_alias=True))


@router.delete("/rules/{rule_id}", response_model=MessageResponse)
async def delete_alert_rule(
    rule_id: str,
    service: AlertService = Depends(get_alert_service),
):
    """Delete an alert rule."""
    deleted = await service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with id '{rule_id}' not found",
        )
    return MessageResponse(message="Alert rule deleted successfully")
