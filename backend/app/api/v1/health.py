"""Health check endpoints."""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_db

router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Readiness check - verifies database connection."""
    try:
        # Ping MongoDB
        await db.command("ping")
        return {
            "status": "ready",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "database": "disconnected",
            "error": str(e),
        }


@router.get("/live")
async def liveness_check():
    """Liveness check."""
    return {"status": "alive"}
