"""Alert service for business logic."""

from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import NotFoundError, ValidationError
from app.models.alert import Alert, AlertRule, AlertSeverity, AlertStatus
from app.repositories.alert_repository import AlertRepository, AlertRuleRepository
from app.schemas.alert import (
    AlertCreate,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertUpdate,
)
from app.schemas.common import PaginatedResponse


class AlertService:
    """Service for alert operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.alert_repo = AlertRepository(db)
        self.rule_repo = AlertRuleRepository(db)

    # Alert operations
    async def create_alert(self, data: AlertCreate) -> Alert:
        """Create a new alert."""
        return await self.alert_repo.create_alert(
            title=data.title,
            source=data.source,
            severity=data.severity,
            description=data.description,
            namespace=data.namespace,
            cluster=data.cluster,
            labels=data.labels,
            metadata=data.metadata,
            rule_id=data.rule_id,
        )

    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get an alert by ID."""
        return await self.alert_repo.get_by_id(alert_id)

    async def get_alerts(
        self,
        status: Optional[AlertStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[Alert]:
        """Get alerts with optional status filter."""
        skip = (page - 1) * page_size

        if status:
            alerts = await self.alert_repo.get_by_status(
                status=status,
                skip=skip,
                limit=page_size,
            )
            total = await self.alert_repo.count({"status": status.value})
        else:
            alerts = await self.alert_repo.get_all(
                skip=skip,
                limit=page_size,
                sort=[("created_at", -1)],
            )
            total = await self.alert_repo.count()

        return PaginatedResponse.create(
            items=alerts,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_alert(
        self,
        alert_id: str,
        data: AlertUpdate,
    ) -> Optional[Alert]:
        """Update an alert."""
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return await self.get_alert(alert_id)
        return await self.alert_repo.update(alert_id, update_data)

    async def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str,
    ) -> Alert:
        """Acknowledge an alert."""
        alert = await self.alert_repo.acknowledge(alert_id, user_id)
        if not alert:
            raise NotFoundError("Alert", alert_id)
        return alert

    async def resolve_alert(self, alert_id: str) -> Alert:
        """Resolve an alert."""
        alert = await self.alert_repo.resolve(alert_id)
        if not alert:
            raise NotFoundError("Alert", alert_id)
        return alert

    async def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
        return await self.alert_repo.get_stats()

    async def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert."""
        return await self.alert_repo.delete(alert_id)

    # Alert Rule operations
    async def create_rule(
        self,
        data: AlertRuleCreate,
        user_id: str,
    ) -> AlertRule:
        """Create a new alert rule."""
        # Check if rule with same name exists
        existing = await self.rule_repo.get_by_name(data.name)
        if existing:
            raise ValidationError(f"Alert rule with name '{data.name}' already exists")

        return await self.rule_repo.create_rule(
            name=data.name,
            user_id=user_id,
            conditions=[c.model_dump() for c in data.conditions],
            severity=data.severity,
            description=data.description,
            enabled=data.enabled,
            namespace_filter=data.namespace_filter,
            cluster_filter=data.cluster_filter,
            labels_filter=data.labels_filter,
            notification_channels=[c.value for c in data.notification_channels],
            cooldown_minutes=data.cooldown_minutes,
        )

    async def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get an alert rule by ID."""
        return await self.rule_repo.get_by_id(rule_id)

    async def get_user_rules(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[AlertRule]:
        """Get alert rules for a user."""
        skip = (page - 1) * page_size
        rules = await self.rule_repo.get_by_user(
            user_id=user_id,
            skip=skip,
            limit=page_size,
        )
        total = await self.rule_repo.count({"user_id": user_id})

        return PaginatedResponse.create(
            items=rules,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_rule(
        self,
        rule_id: str,
        data: AlertRuleUpdate,
    ) -> Optional[AlertRule]:
        """Update an alert rule."""
        update_data = data.model_dump(exclude_none=True)

        # Convert conditions if present
        if "conditions" in update_data:
            update_data["conditions"] = [
                c.model_dump() if hasattr(c, "model_dump") else c
                for c in update_data["conditions"]
            ]

        # Convert notification channels if present
        if "notification_channels" in update_data:
            update_data["notification_channels"] = [
                c.value if hasattr(c, "value") else c
                for c in update_data["notification_channels"]
            ]

        from datetime import datetime, timezone
        update_data["updated_at"] = datetime.now(timezone.utc)

        return await self.rule_repo.update(rule_id, update_data)

    async def toggle_rule(
        self,
        rule_id: str,
        enabled: bool,
    ) -> Optional[AlertRule]:
        """Enable or disable an alert rule."""
        return await self.rule_repo.set_enabled(rule_id, enabled)

    async def delete_rule(self, rule_id: str) -> bool:
        """Delete an alert rule."""
        return await self.rule_repo.delete(rule_id)

    async def get_enabled_rules(self) -> List[AlertRule]:
        """Get all enabled alert rules."""
        return await self.rule_repo.get_enabled_rules()
