"""Main API router for v1."""

from fastapi import APIRouter

from app.api.v1 import alerts, auth, health, logs, metrics

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
