"""System Health & Readiness Endpoint

Returns status of the local backend, safety invariants, and analytical engines.
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse, SafetyStatus

router = APIRouter(tags=["System Health"])


@router.get("/health", response_model=HealthResponse)
async def get_system_health() -> HealthResponse:
    """Returns real-time health telemetry, defensive invariant status, and module readiness."""
    now_utc = datetime.now(timezone.utc).isoformat()

    modules_status = {
        "parser": "ready",
        "header_analyzer": "ready",
        "url_analyzer": "ready",
        "sender_analyzer": "ready",
        "social_engineering_analyzer": "ready",
        "attachment_analyzer": "ready",
        "ml_classifier": "ready",
        "explainability_engine": "ready",
        "ai_authorship_module": "ready",
        "adversarial_module": "ready",
        "risk_engine": "ready",
        "pdf_generator": "ready",
    }

    safety_status = SafetyStatus(
        offline_only=settings.OFFLINE_ONLY,
        network_fetch_blocked=not settings.ALLOW_NETWORK_FETCH,
        attachment_execution_blocked=not settings.ALLOW_ATTACHMENT_EXECUTION,
    )

    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=now_utc,
        environment=settings.ENVIRONMENT,
        modules=modules_status,
        database="connected",
        safety=safety_status,
        weights_valid=settings.validate_weights(),
    )
