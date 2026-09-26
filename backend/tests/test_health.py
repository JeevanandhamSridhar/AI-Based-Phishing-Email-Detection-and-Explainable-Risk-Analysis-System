"""Unit Tests for Core Application & Health Telemetry
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_root_endpoint():
    """Verify that root endpoint returns application metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION
    assert data["safety_mode"] == "defensive-static-only"
    assert "docs" in data


def test_health_endpoint_structure():
    """Verify health endpoint returns complete telemetry and module readiness."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["version"] == settings.VERSION
    assert "timestamp" in data
    assert data["environment"] == settings.ENVIRONMENT
    assert data["database"] == "connected"
    assert data["weights_valid"] is True

    # Validate modules readiness
    expected_modules = [
        "parser",
        "header_analyzer",
        "url_analyzer",
        "sender_analyzer",
        "social_engineering_analyzer",
        "attachment_analyzer",
        "ml_classifier",
        "explainability_engine",
        "ai_authorship_module",
        "adversarial_module",
        "risk_engine",
        "pdf_generator",
    ]
    for mod in expected_modules:
        assert mod in data["modules"]
        assert data["modules"][mod] == "ready"

    # Validate safety invariants
    safety = data["safety"]
    assert safety["offline_only"] is True
    assert safety["network_fetch_blocked"] is True
    assert safety["attachment_execution_blocked"] is True


def test_cors_headers():
    """Verify CORS headers allow trusted local origins."""
    headers = {"Origin": "http://localhost:5173"}
    response = client.get("/api/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_settings_weight_validation():
    """Verify that the risk weights configuration validates sum to 100.0."""
    assert settings.validate_weights() is True


def test_custom_error_handling():
    """Verify that AppBaseException returns a standardized error envelope."""
    from app.core.errors import ParsingError
    from fastapi import APIRouter

    dummy_router = APIRouter()

    @dummy_router.get("/test-error")
    async def trigger_error():
        raise ParsingError("Corrupted MIME boundary", details={"offset": 104})

    app.include_router(dummy_router)
    response = client.get("/test-error")
    assert response.status_code == 422
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["code"] == "EMAIL_PARSING_ERROR"
    assert payload["error"]["message"] == "Corrupted MIME boundary"
    assert payload["error"]["details"]["offset"] == 104

