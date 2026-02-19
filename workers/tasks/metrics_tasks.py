"""Tasks for processing metrics."""

import asyncio
from datetime import datetime, timezone
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
def process_metrics(self):
    """Process incoming metrics from the queue."""
    try:
        logger.info("Processing metrics batch")
        db = get_db()

        # Get unprocessed metrics (you would typically get these from RabbitMQ)
        # This is a placeholder - in real implementation, consume from message queue
        metrics_count = db.metrics.count_documents(
            {"processed": {"$exists": False}}
        )

        if metrics_count > 0:
            # Mark metrics as processed
            db.metrics.update_many(
                {"processed": {"$exists": False}},
                {"$set": {"processed": True, "processed_at": datetime.now(timezone.utc)}}
            )
            logger.info(f"Processed {metrics_count} metrics")

        return {"processed": metrics_count}

    except Exception as exc:
        logger.error(f"Error processing metrics: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def aggregate_metrics(self, metric_type: str, time_window: str = "1h"):
    """Aggregate metrics for a given type and time window."""
    try:
        logger.info(f"Aggregating {metric_type} metrics for {time_window}")
        db = get_db()

        # Calculate time window
        from datetime import timedelta
        windows = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
        }
        delta = windows.get(time_window, timedelta(hours=1))
        start_time = datetime.now(timezone.utc) - delta

        # Run aggregation
        pipeline = [
            {
                "$match": {
                    "metric_type": metric_type,
                    "timestamp": {"$gte": start_time},
                }
            },
            {
                "$group": {
                    "_id": {"source": "$source", "name": "$name"},
                    "avg_value": {"$avg": "$value"},
                    "min_value": {"$min": "$value"},
                    "max_value": {"$max": "$value"},
                    "count": {"$sum": 1},
                }
            },
        ]

        results = list(db.metrics.aggregate(pipeline))
        logger.info(f"Aggregated {len(results)} metric groups")

        return {"aggregations": len(results), "time_window": time_window}

    except Exception as exc:
        logger.error(f"Error aggregating metrics: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def ingest_metric(metric_data: Dict[str, Any]):
    """Ingest a single metric."""
    try:
        logger.debug(f"Ingesting metric: {metric_data.get('name')}")
        db = get_db()

        metric_data["timestamp"] = datetime.now(timezone.utc)
        metric_data["processed"] = False

        db.metrics.insert_one(metric_data)
        return {"status": "success", "metric": metric_data.get("name")}

    except Exception as exc:
        logger.error(f"Error ingesting metric: {exc}")
        raise


@shared_task
def ingest_metrics_batch(metrics: List[Dict[str, Any]]):
    """Ingest a batch of metrics."""
    try:
        logger.info(f"Ingesting batch of {len(metrics)} metrics")
        db = get_db()

        now = datetime.now(timezone.utc)
        for metric in metrics:
            metric["timestamp"] = metric.get("timestamp", now)
            metric["processed"] = False

        if metrics:
            db.metrics.insert_many(metrics)

        return {"status": "success", "count": len(metrics)}

    except Exception as exc:
        logger.error(f"Error ingesting metrics batch: {exc}")
        raise
