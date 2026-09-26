"""Main API Router Aggregator

Mounts all sub-routers under the `/api` prefix.
"""

from fastapi import APIRouter
from app.api.endpoints import health

api_router = APIRouter()

# Mount health endpoint
api_router.include_router(health.router)
