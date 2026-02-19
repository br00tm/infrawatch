"""Tasks for processing alerts."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from celery import shared_task
from celery.utils.log import get_task_logger
from pymongo import MongoClient

from config import get_settings
from utils.notification import send_notification

logger = get_task_logger(__name__)
settings = get_settings()


def get_db():
    """Get MongoDB database connection."""
    client = MongoClient(settings.mongodb_url)
    return client[settings.mongodb_db_name]


@shared_task(bind=True, max_retries=3)
def check_alert_rules(self):
    """Check all enabled alert rules against current metrics."""
    try:
        logger.info("Checking alert rules")
        db = get_db()

        # Get enabled rules
        rules = list(db.alert_rules.find({"enabled": True}))
        logger.info(f"Found {len(rules)} enabled alert rules")

        alerts_created = 0
        for rule in rules:
            try:
                alert_triggered = evaluate_rule(db, rule)
                if alert_triggered:
                    alerts_created += 1
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.get('name')}: {e}")

        return {"rules_checked": len(rules), "alerts_created": alerts_created}

    except Exception as exc:
        logger.error(f"Error checking alert rules: {exc}")
        raise self.retry(exc=exc, countdown=60)


def evaluate_rule(db, rule: Dict[str, Any]) -> bool:
    """Evaluate a single alert rule."""
    # Check cooldown
    last_triggered = rule.get("last_triggered")
    if last_triggered:
        cooldown = timedelta(minutes=rule.get("cooldown_minutes", 5))
        if datetime.now(timezone.utc) - last_triggered < cooldown:
            return False

    # Check conditions
    conditions = rule.get("conditions", [])
    all_conditions_met = True

    for condition in conditions:
        metric_name = condition.get("metric_name")
        operator = condition.get("operator")
        threshold = condition.get("threshold")
        duration = condition.get("duration_seconds", 60)

        # Query recent metrics
        start_time = datetime.now(timezone.utc) - timedelta(seconds=duration)
        metrics = list(db.metrics.find({
            "name": metric_name,
            "timestamp": {"$gte": start_time},
        }).sort("timestamp", -1).limit(10))

        if not metrics:
            all_conditions_met = False
            break

        # Evaluate condition
        avg_value = sum(m["value"] for m in metrics) / len(metrics)
        condition_met = evaluate_condition(avg_value, operator, threshold)

        if not condition_met:
            all_conditions_met = False
            break

    if all_conditions_met:
        # Create alert
        alert = {
            "title": f"Alert: {rule.get('name')}",
            "description": rule.get("description"),
            "severity": rule.get("severity", "warning"),
            "status": "active",
            "source": "alert_rule",
            "rule_id": str(rule.get("_id")),
            "labels": rule.get("labels_filter", {}),
            "created_at": datetime.now(timezone.utc),
        }
        db.alerts.insert_one(alert)

        # Update last triggered
        db.alert_rules.update_one(
            {"_id": rule["_id"]},
            {"$set": {"last_triggered": datetime.now(timezone.utc)}}
        )

        # Send notifications
        channels = rule.get("notification_channels", [])
        send_alert_notifications.delay(alert, channels)

        return True

    return False


def evaluate_condition(value: float, operator: str, threshold: float) -> bool:
    """Evaluate a single condition."""
    operators = {
        "gt": lambda v, t: v > t,
        "lt": lambda v, t: v < t,
        "gte": lambda v, t: v >= t,
        "lte": lambda v, t: v <= t,
        "eq": lambda v, t: v == t,
        "ne": lambda v, t: v != t,
    }
    op_func = operators.get(operator, lambda v, t: False)
    return op_func(value, threshold)


@shared_task(bind=True, max_retries=3)
def send_alert_notifications(self, alert: Dict[str, Any], channels: list):
    """Send alert notifications to specified channels."""
    try:
        logger.info(f"Sending alert notifications for: {alert.get('title')}")

        for channel in channels:
            try:
                message = format_alert_message(alert)
                send_notification(channel, message)
                logger.info(f"Sent notification to {channel}")
            except Exception as e:
                logger.error(f"Failed to send notification to {channel}: {e}")

        return {"status": "success", "channels": channels}

    except Exception as exc:
        logger.error(f"Error sending notifications: {exc}")
        raise self.retry(exc=exc, countdown=30)


def format_alert_message(alert: Dict[str, Any]) -> str:
    """Format alert for notification."""
    severity_emoji = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "🔴",
        "critical": "🚨",
    }
    emoji = severity_emoji.get(alert.get("severity", "warning"), "⚠️")

    return f"""
{emoji} **{alert.get('title')}**

**Severity:** {alert.get('severity', 'unknown').upper()}
**Source:** {alert.get('source', 'unknown')}
**Description:** {alert.get('description', 'No description')}
**Time:** {alert.get('created_at', 'Unknown')}
"""
