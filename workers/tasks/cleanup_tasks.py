"""Tasks for cleaning up old data."""

from datetime import datetime, timedelta, timezone

from celery import shared_task
from celery.utils.log import get_task_logger
from pymongo import MongoClient

from config import get_settings

logger = get_task_logger(__name__)
settings = get_settings()


def get_db():
    """Get MongoDB database connection."""
    client = MongoClient(settings.mongodb_url)
    return client[settings.mongodb_db_name]


@shared_task(bind=True, max_retries=3)
def cleanup_old_data(self):
    """Clean up old data from all collections."""
    try:
        logger.info("Starting cleanup of old data")
        db = get_db()

        results = {}

        # Cleanup metrics (older than 7 days)
        metrics_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        metrics_result = db.metrics.delete_many({"timestamp": {"$lt": metrics_cutoff}})
        results["metrics_deleted"] = metrics_result.deleted_count
        logger.info(f"Deleted {metrics_result.deleted_count} old metrics")

        # Cleanup logs (older than 30 days)
        logs_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        logs_result = db.logs.delete_many({"timestamp": {"$lt": logs_cutoff}})
        results["logs_deleted"] = logs_result.deleted_count
        logger.info(f"Deleted {logs_result.deleted_count} old logs")

        # Cleanup resolved alerts (older than 90 days)
        alerts_cutoff = datetime.now(timezone.utc) - timedelta(days=90)
        alerts_result = db.alerts.delete_many({
            "status": "resolved",
            "resolved_at": {"$lt": alerts_cutoff},
        })
        results["alerts_deleted"] = alerts_result.deleted_count
        logger.info(f"Deleted {alerts_result.deleted_count} old resolved alerts")

        # Cleanup log stats (older than 7 days)
        stats_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        stats_result = db.log_stats.delete_many({"timestamp": {"$lt": stats_cutoff}})
        results["stats_deleted"] = stats_result.deleted_count
        logger.info(f"Deleted {stats_result.deleted_count} old log stats")

        return results

    except Exception as exc:
        logger.error(f"Error during cleanup: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=3)
def cleanup_metrics(self, days: int = 7):
    """Clean up metrics older than specified days."""
    try:
        logger.info(f"Cleaning up metrics older than {days} days")
        db = get_db()

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = db.metrics.delete_many({"timestamp": {"$lt": cutoff}})

        logger.info(f"Deleted {result.deleted_count} old metrics")
        return {"deleted": result.deleted_count}

    except Exception as exc:
        logger.error(f"Error cleaning up metrics: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def cleanup_logs(self, days: int = 30):
    """Clean up logs older than specified days."""
    try:
        logger.info(f"Cleaning up logs older than {days} days")
        db = get_db()

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = db.logs.delete_many({"timestamp": {"$lt": cutoff}})

        logger.info(f"Deleted {result.deleted_count} old logs")
        return {"deleted": result.deleted_count}

    except Exception as exc:
        logger.error(f"Error cleaning up logs: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def compact_database():
    """Run MongoDB compact operation on collections."""
    try:
        logger.info("Running database compaction")
        db = get_db()

        collections = ["metrics", "logs", "alerts"]
        results = {}

        for collection in collections:
            try:
                db.command("compact", collection)
                results[collection] = "success"
                logger.info(f"Compacted collection: {collection}")
            except Exception as e:
                results[collection] = f"failed: {str(e)}"
                logger.error(f"Failed to compact {collection}: {e}")

        return results

    except Exception as exc:
        logger.error(f"Error during compaction: {exc}")
        raise
