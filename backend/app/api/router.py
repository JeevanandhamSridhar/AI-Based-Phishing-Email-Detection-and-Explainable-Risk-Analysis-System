"""Main API Router Aggregator

Mounts all sub-routers under the `/api` prefix.
"""

from fastapi import APIRouter
from app.api.endpoints import health, analyze, history, models, samples

api_router = APIRouter()

# Mount all endpoint routers
api_router.include_router(health.router)
api_router.include_router(analyze.router)
api_router.include_router(history.router)
api_router.include_router(models.router)
api_router.include_router(samples.router)
