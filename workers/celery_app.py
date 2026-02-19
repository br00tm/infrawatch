"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from config import get_settings

settings = get_settings()

app = Celery(
    "infrawatch",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "tasks.metrics_tasks",
        "tasks.alerts_tasks",
        "tasks.logs_tasks",
        "tasks.cleanup_tasks",
        "tasks.health_tasks",
    ],
)

# Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.task_timeout,
    worker_prefetch_multiplier=1,
    worker_concurrency=settings.worker_concurrency,
)

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Process metrics every 30 seconds
    "process-metrics": {
        "task": "tasks.metrics_tasks.process_metrics",
        "schedule": 30.0,
    },
    # Check alerts every minute
    "check-alerts": {
        "task": "tasks.alerts_tasks.check_alert_rules",
        "schedule": 60.0,
    },
    # Aggregate logs every 5 minutes
    "aggregate-logs": {
        "task": "tasks.logs_tasks.aggregate_logs",
        "schedule": 300.0,
    },
    # Cleanup old data daily at 3 AM
    "cleanup-old-data": {
        "task": "tasks.cleanup_tasks.cleanup_old_data",
        "schedule": crontab(hour=3, minute=0),
    },
    # Health check every minute
    "health-check": {
        "task": "tasks.health_tasks.check_system_health",
        "schedule": 60.0,
    },
}

if __name__ == "__main__":
    app.start()
