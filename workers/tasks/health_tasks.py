"""Tasks for health checks."""

from datetime import datetime, timezone

from celery import shared_task
from celery.utils.log import get_task_logger
from pymongo import MongoClient
import redis

from config import get_settings

logger = get_task_logger(__name__)
settings = get_settings()


def get_db():
    """Get MongoDB database connection."""
    client = MongoClient(settings.mongodb_url)
    return client[settings.mongodb_db_name]


@shared_task
def check_system_health():
    """Check health of all system components."""
    try:
        logger.info("Running system health check")
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
        }

        # Check MongoDB
        try:
            client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            health_status["components"]["mongodb"] = {
                "status": "healthy",
                "response_time_ms": 0,  # Would measure actual response time
            }
        except Exception as e:
            health_status["components"]["mongodb"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            logger.error(f"MongoDB health check failed: {e}")

        # Check Redis
        try:
            r = redis.from_url(settings.redis_url, socket_timeout=5)
            r.ping()
            health_status["components"]["redis"] = {
                "status": "healthy",
                "response_time_ms": 0,
            }
        except Exception as e:
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "error": str(e),
            }
            logger.error(f"Redis health check failed: {e}")

        # Store health status
        try:
            db = get_db()
            db.health_checks.insert_one({
                "timestamp": datetime.now(timezone.utc),
                **health_status,
            })
        except Exception as e:
            logger.error(f"Failed to store health check: {e}")

        # Determine overall status
        all_healthy = all(
            c.get("status") == "healthy"
            for c in health_status["components"].values()
        )
        health_status["overall"] = "healthy" if all_healthy else "degraded"

        return health_status

    except Exception as exc:
        logger.error(f"Error during health check: {exc}")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall": "error",
            "error": str(exc),
        }


@shared_task
def check_mongodb_health():
    """Check MongoDB connection health."""
    try:
        client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return {"status": "healthy", "component": "mongodb"}
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return {"status": "unhealthy", "component": "mongodb", "error": str(e)}


@shared_task
def check_redis_health():
    """Check Redis connection health."""
    try:
        r = redis.from_url(settings.redis_url, socket_timeout=5)
        r.ping()
        return {"status": "healthy", "component": "redis"}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {"status": "unhealthy", "component": "redis", "error": str(e)}


@shared_task
def get_system_stats():
    """Get system statistics."""
    try:
        db = get_db()

        stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "collections": {},
        }

        # Get collection stats
        for collection in ["metrics", "logs", "alerts", "users", "alert_rules"]:
            try:
                count = db[collection].count_documents({})
                stats["collections"][collection] = {"count": count}
            except Exception as e:
                stats["collections"][collection] = {"error": str(e)}

        return stats

    except Exception as exc:
        logger.error(f"Error getting system stats: {exc}")
        return {"error": str(exc)}
