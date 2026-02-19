"""Alert repository for database operations."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from app.models.alert import Alert, AlertRule, AlertSeverity, AlertStatus
from app.repositories.base_repository import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    """Repository for alert operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "alerts", Alert)

    async def create_alert(
        self,
        title: str,
        source: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        description: Optional[str] = None,
        namespace: str = "default",
        cluster: str = "default",
        labels: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        rule_id: Optional[str] = None,
    ) -> Alert:
        """Create a new alert."""
        alert_data = {
            "title": title,
            "description": description,
            "severity": severity.value if isinstance(severity, AlertSeverity) else severity,
            "status": AlertStatus.ACTIVE.value,
            "source": source,
            "namespace": namespace,
            "cluster": cluster,
            "labels": labels or {},
            "metadata": metadata or {},
            "rule_id": rule_id,
            "created_at": datetime.now(timezone.utc),
        }
        return await self.create(alert_data)

    async def get_active_alerts(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Alert]:
        """Get active alerts."""
        return await self.get_all(
            filter={"status": AlertStatus.ACTIVE.value},
            skip=skip,
            limit=limit,
            sort=[("created_at", DESCENDING)],
        )

    async def get_by_status(
        self,
        status: AlertStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Alert]:
        """Get alerts by status."""
        return await self.get_all(
            filter={"status": status.value},
            skip=skip,
            limit=limit,
            sort=[("created_at", DESCENDING)],
        )

    async def acknowledge(
        self,
        alert_id: str,
        user_id: str,
    ) -> Optional[Alert]:
        """Acknowledge an alert."""
        return await self.update(
            alert_id,
            {
                "status": AlertStatus.ACKNOWLEDGED.value,
                "acknowledged_by": user_id,
                "acknowledged_at": datetime.now(timezone.utc),
            },
        )

    async def resolve(self, alert_id: str) -> Optional[Alert]:
        """Resolve an alert."""
        return await self.update(
            alert_id,
            {
                "status": AlertStatus.RESOLVED.value,
                "resolved_at": datetime.now(timezone.utc),
            },
        )

    async def silence(self, alert_id: str) -> Optional[Alert]:
        """Silence an alert."""
        return await self.update(
            alert_id,
            {"status": AlertStatus.SILENCED.value},
        )

    async def get_stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
        pipeline = [
            {
                "$facet": {
                    "by_status": [
                        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                    ],
                    "by_severity": [
                        {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
                    ],
                    "by_source": [
                        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 10},
                    ],
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)

        if not result:
            return {
                "total_active": 0,
                "total_acknowledged": 0,
                "total_resolved": 0,
                "by_severity": {},
                "by_source": {},
            }

        data = result[0]
        status_counts = {item["_id"]: item["count"] for item in data["by_status"]}

        return {
            "total_active": status_counts.get(AlertStatus.ACTIVE.value, 0),
            "total_acknowledged": status_counts.get(AlertStatus.ACKNOWLEDGED.value, 0),
            "total_resolved": status_counts.get(AlertStatus.RESOLVED.value, 0),
            "by_severity": {item["_id"]: item["count"] for item in data["by_severity"]},
            "by_source": {item["_id"]: item["count"] for item in data["by_source"]},
        }


class AlertRuleRepository(BaseRepository[AlertRule]):
    """Repository for alert rule operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "alert_rules", AlertRule)

    async def create_rule(
        self,
        name: str,
        user_id: str,
        conditions: List[Dict[str, Any]],
        severity: AlertSeverity = AlertSeverity.WARNING,
        description: Optional[str] = None,
        enabled: bool = True,
        namespace_filter: Optional[str] = None,
        cluster_filter: Optional[str] = None,
        labels_filter: Optional[Dict[str, str]] = None,
        notification_channels: Optional[List[str]] = None,
        cooldown_minutes: int = 5,
    ) -> AlertRule:
        """Create a new alert rule."""
        now = datetime.now(timezone.utc)
        rule_data = {
            "name": name,
            "description": description,
            "enabled": enabled,
            "severity": severity.value if isinstance(severity, AlertSeverity) else severity,
            "conditions": conditions,
            "namespace_filter": namespace_filter,
            "cluster_filter": cluster_filter,
            "labels_filter": labels_filter or {},
            "notification_channels": notification_channels or [],
            "cooldown_minutes": cooldown_minutes,
            "user_id": user_id,
            "last_triggered": None,
            "created_at": now,
            "updated_at": now,
        }
        return await self.create(rule_data)

    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AlertRule]:
        """Get alert rules by user."""
        return await self.get_all(
            filter={"user_id": user_id},
            skip=skip,
            limit=limit,
            sort=[("created_at", DESCENDING)],
        )

    async def get_enabled_rules(self) -> List[AlertRule]:
        """Get all enabled rules."""
        return await self.get_all(
            filter={"enabled": True},
            limit=1000,
        )

    async def get_by_name(self, name: str) -> Optional[AlertRule]:
        """Get rule by name."""
        doc = await self.collection.find_one({"name": name})
        if doc:
            return AlertRule.from_mongo(doc)
        return None

    async def set_enabled(
        self,
        rule_id: str,
        enabled: bool,
    ) -> Optional[AlertRule]:
        """Enable or disable a rule."""
        return await self.update(
            rule_id,
            {
                "enabled": enabled,
                "updated_at": datetime.now(timezone.utc),
            },
        )

    async def update_last_triggered(self, rule_id: str) -> Optional[AlertRule]:
        """Update last triggered timestamp."""
        return await self.update(
            rule_id,
            {"last_triggered": datetime.now(timezone.utc)},
        )
