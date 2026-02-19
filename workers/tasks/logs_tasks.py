"""Tasks for processing logs."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

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
def aggregate_logs(self):
    """Aggregate log statistics."""
    try:
        logger.info("Aggregating log statistics")
        db = get_db()

        # Aggregate last hour
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)

        pipeline = [
            {"$match": {"timestamp": {"$gte": start_time}}},
            {
                "$facet": {
                    "by_level": [
                        {"$group": {"_id": "$level", "count": {"$sum": 1}}}
                    ],
                    "by_source": [
                        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 20},
                    ],
                    "total": [{"$count": "count"}],
                }
            },
        ]

        result = list(db.logs.aggregate(pipeline))

        if result:
            stats = result[0]
            # Store aggregation results
            db.log_stats.insert_one({
                "timestamp": datetime.now(timezone.utc),
                "period": "1h",
                "by_level": {item["_id"]: item["count"] for item in stats.get("by_level", [])},
                "by_source": {item["_id"]: item["count"] for item in stats.get("by_source", [])},
                "total": stats.get("total", [{}])[0].get("count", 0),
            })

        return {"status": "success"}

    except Exception as exc:
        logger.error(f"Error aggregating logs: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def ingest_log(log_data: Dict[str, Any]):
    """Ingest a single log entry."""
    try:
        logger.debug(f"Ingesting log from: {log_data.get('source')}")
        db = get_db()

        log_data["timestamp"] = log_data.get("timestamp", datetime.now(timezone.utc))

        db.logs.insert_one(log_data)
        return {"status": "success"}

    except Exception as exc:
        logger.error(f"Error ingesting log: {exc}")
        raise


@shared_task
def ingest_logs_batch(logs: List[Dict[str, Any]]):
    """Ingest a batch of log entries."""
    try:
        logger.info(f"Ingesting batch of {len(logs)} logs")
        db = get_db()

        now = datetime.now(timezone.utc)
        for log in logs:
            log["timestamp"] = log.get("timestamp", now)

        if logs:
            db.logs.insert_many(logs)

        return {"status": "success", "count": len(logs)}

    except Exception as exc:
        logger.error(f"Error ingesting logs batch: {exc}")
        raise


@shared_task(bind=True, max_retries=3)
def analyze_error_patterns(self):
    """Analyze error log patterns for anomaly detection."""
    try:
        logger.info("Analyzing error patterns")
        db = get_db()

        # Get error logs from last hour
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)

        error_logs = list(db.logs.find({
            "level": {"$in": ["error", "critical"]},
            "timestamp": {"$gte": start_time},
        }))

        # Group by source
        error_counts = {}
        for log in error_logs:
            source = log.get("source", "unknown")
            error_counts[source] = error_counts.get(source, 0) + 1

        # Check for anomalies (simple threshold)
        anomalies = []
        for source, count in error_counts.items():
            if count > 10:  # Threshold for anomaly
                anomalies.append({"source": source, "error_count": count})
                logger.warning(f"Anomaly detected: {source} has {count} errors in last hour")

        return {"errors_analyzed": len(error_logs), "anomalies": anomalies}

    except Exception as exc:
        logger.error(f"Error analyzing patterns: {exc}")
        raise self.retry(exc=exc, countdown=60)
