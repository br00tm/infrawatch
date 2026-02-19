"""MongoDB index definitions."""

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.logging import get_logger

logger = get_logger(__name__)


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create all indexes for the database."""
    logger.info("Creating database indexes...")

    # Users collection indexes
    users_indexes = [
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("username", ASCENDING)], unique=True),
        IndexModel([("created_at", DESCENDING)]),
    ]
    await db.users.create_indexes(users_indexes)

    # Metrics collection indexes
    metrics_indexes = [
        IndexModel([("timestamp", DESCENDING)]),
        IndexModel([("source", ASCENDING), ("timestamp", DESCENDING)]),
        IndexModel([("metric_type", ASCENDING), ("timestamp", DESCENDING)]),
        IndexModel([("namespace", ASCENDING), ("timestamp", DESCENDING)]),
        IndexModel(
            [("timestamp", ASCENDING)],
            expireAfterSeconds=604800,  # 7 days TTL
            name="timestamp_1",
        ),
    ]
    await db.metrics.create_indexes(metrics_indexes)

    # Logs collection indexes
    logs_indexes = [
        IndexModel([("timestamp", DESCENDING)]),
        IndexModel([("level", ASCENDING), ("timestamp", DESCENDING)]),
        IndexModel([("source", ASCENDING), ("timestamp", DESCENDING)]),
        IndexModel([("namespace", ASCENDING), ("timestamp", DESCENDING)]),
        IndexModel(
            [("message", "text"), ("source", "text")],
            name="message_text_source_text",
        ),
        IndexModel(
            [("timestamp", ASCENDING)],
            expireAfterSeconds=2592000,  # 30 days TTL
            name="timestamp_1",
        ),
    ]
    await db.logs.create_indexes(logs_indexes)

    # Alerts collection indexes
    alerts_indexes = [
        IndexModel([("created_at", DESCENDING)]),
        IndexModel([("status", ASCENDING), ("created_at", DESCENDING)]),
        IndexModel([("severity", ASCENDING), ("created_at", DESCENDING)]),
        IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
    ]
    await db.alerts.create_indexes(alerts_indexes)

    # Alert rules collection indexes
    alert_rules_indexes = [
        IndexModel([("name", ASCENDING)], unique=True),
        IndexModel([("enabled", ASCENDING)]),
        IndexModel([("user_id", ASCENDING)]),
    ]
    await db.alert_rules.create_indexes(alert_rules_indexes)

    logger.info("Database indexes created successfully")
