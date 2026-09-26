"""Comprehensive Integration Tests for REST API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

PHISHING_SAMPLE = (
    "From: PayPal Account Security <security@paypa1-update.com>\n"
    "To: victim@example.com\n"
    "Subject: URGENT: Your PayPal Account Has Been Suspended\n"
    "Authentication-Results: spf=fail; dkim=none; dmarc=fail\n"
    "Reply-To: attacker@mail-collector.ru\n"
    "\n"
    "Dear Customer,\n"
    "We detected unauthorized access on your account. Immediate action required!\n"
    "Click here to verify your credentials within 24 hours: http://paypal.com.verify-billing.xyz/auth\n"
)

LEGITIMATE_SAMPLE = (
    "From: HR Department <hr@acme-corp.com>\n"
    "To: employee@acme-corp.com\n"
    "Subject: Benefits Open Enrollment Period\n"
    "Authentication-Results: spf=pass; dkim=pass; dmarc=pass\n"
    "\n"
    "Hi Team,\n"
    "Benefits open enrollment begins next Monday. Please review the updated handbook on the intranet: https://intranet.company.com/portal\n"
    "Best regards,\nHuman Resources\n"
)


def test_analyze_phishing_email_json():
    """Verify POST /api/analyze correctly assesses phishing email with high risk and full telemetry."""
    response = client.post("/api/analyze", json={"raw_email": PHISHING_SAMPLE})
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["overall_risk"]["score"] >= 70.0
    assert data["overall_risk"]["severity"] in ("HIGH", "CRITICAL")

    # Check 7 factor breakdown keys
    factors = data["factor_breakdown"]
    expected_factors = ["ml_phishing", "url_risk", "header_auth", "sender_domain", "social_engineering", "attachment_risk", "content_anomalies"]
    for f in expected_factors:
        assert f in factors
        assert "weighted_contribution" in factors[f]

    # Check Explainability
    xai = data["explainability"]
    assert len(xai["human_readable_summary"]) > 20
    assert "caveat" in xai

    # Check AI Authorship
    authorship = data["ai_authorship"]
    assert 0.0 <= authorship["ai_generated_likelihood"] <= 100.0
    assert "caveat" in authorship


def test_analyze_legitimate_email_json():
    """Verify POST /api/analyze correctly classifies benign communication as LOW risk."""
    response = client.post("/api/analyze", json={"raw_email": LEGITIMATE_SAMPLE})
    assert response.status_code == 200
    data = response.json()

    assert data["overall_risk"]["score"] < 35.0
    assert data["overall_risk"]["severity"] in ("LOW", "MODERATE")


def test_analyze_empty_payload_error():
    """Verify validation error on empty payload."""
    response = client.post("/api/analyze", json={"raw_email": ""})
    assert response.status_code == 422
    payload = response.json()
    assert "error" in payload


def test_get_history_endpoints():
    """Verify GET /api/history returns triage ledger and GET /api/history/{id} returns details."""
    # Run an analysis first to ensure at least one record
    client.post("/api/analyze", json={"raw_email": PHISHING_SAMPLE})

    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    items = hist_res.json()
    assert len(items) >= 1

    first_id = items[0]["id"]
    detail_res = client.get(f"/api/history/{first_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == first_id
    assert "overall_risk" in detail


def test_get_models_performance():
    """Verify GET /api/models/performance returns genuine evaluation metrics."""
    response = client.get("/api/models/performance")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "evaluation" in data
    eval_m = data["evaluation"]
    assert "metrics" in eval_m or "accuracy" in eval_m


def test_get_authorship_evaluation():
    """Verify GET /api/authorship/evaluate returns Module A cross-generator telemetry."""
    response = client.get("/api/authorship/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    metrics = data["metrics"]
    assert "cross_generator_metrics" in metrics


def test_get_adversarial_evaluation():
    """Verify GET /api/adversarial/evaluate returns Module B evasion test results."""
    response = client.get("/api/adversarial/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "ml_evasion_rate_pct" in data["results"]


def test_get_preset_samples():
    """Verify GET /api/samples returns demonstration presets."""
    response = client.get("/api/samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 6
    for s in samples:
        assert "filename" in s
        assert "raw_content" in s
        assert "subject" in s
