"""Unit Tests for Multi-Factor Hybrid Risk Engine

Includes mandatory boundary testing at 0, 24, 25, 49, 50, 74, 75, 100.
"""

import pytest
from app.services.risk_engine import RiskEngine, evaluate_content_anomalies
from app.analyzers.url_analyzer import URLAnalysisResult
from app.analyzers.header_analyzer import HeaderAnalysisResult
from app.analyzers.sender_analyzer import SenderAnalysisResult
from app.analyzers.social_engineering_analyzer import SocialEngineeringResult
from app.analyzers.attachment_analyzer import AttachmentAnalysisResult


@pytest.fixture
def engine():
    return RiskEngine()


def test_boundary_severity_tiers(engine):
    """Verify exact categorization at critical boundary scores: 0, 24, 25, 49, 50, 74, 75, 100."""
    # 0.0 -> LOW
    sev, bracket = engine.classify_severity(0.0)
    assert sev == "LOW"
    assert bracket == "0-24"

    # 24.0 -> LOW
    sev, bracket = engine.classify_severity(24.0)
    assert sev == "LOW"
    assert bracket == "0-24"

    # 24.9 -> LOW
    sev, bracket = engine.classify_severity(24.9)
    assert sev == "LOW"

    # 25.0 -> MODERATE
    sev, bracket = engine.classify_severity(25.0)
    assert sev == "MODERATE"
    assert bracket == "25-49"

    # 49.0 -> MODERATE
    sev, bracket = engine.classify_severity(49.0)
    assert sev == "MODERATE"
    assert bracket == "25-49"

    # 50.0 -> HIGH
    sev, bracket = engine.classify_severity(50.0)
    assert sev == "HIGH"
    assert bracket == "50-74"

    # 74.0 -> HIGH
    sev, bracket = engine.classify_severity(74.0)
    assert sev == "HIGH"
    assert bracket == "50-74"

    # 75.0 -> CRITICAL
    sev, bracket = engine.classify_severity(75.0)
    assert sev == "CRITICAL"
    assert bracket == "75-100"

    # 100.0 -> CRITICAL
    sev, bracket = engine.classify_severity(100.0)
    assert sev == "CRITICAL"
    assert bracket == "75-100"


def test_full_clean_email_risk(engine):
    """Verify completely clean email yields near-zero score and LOW severity."""
    res = engine.compute_risk(
        ml_prob=0.0,
        url_res=URLAnalysisResult(score=0.0),
        header_res=HeaderAnalysisResult(score=0.0),
        sender_res=SenderAnalysisResult(score=0.0),
        social_res=SocialEngineeringResult(score=0.0),
        attach_res=AttachmentAnalysisResult(score=0.0),
        body_plain="Standard business memo",
    )
    assert res.score == 0.0
    assert res.severity == "LOW"


def test_severe_multi_vector_attack_risk(engine):
    """Verify compound phishing attack triggers CRITICAL severity."""
    res = engine.compute_risk(
        ml_prob=0.98,  # ML: 30 * 0.98 = 29.4
        url_res=URLAnalysisResult(score=90.0),  # URL: 20 * 0.9 = 18.0
        header_res=HeaderAnalysisResult(score=85.0),  # Header: 15 * 0.85 = 12.75
        sender_res=SenderAnalysisResult(score=95.0, is_impersonation=True),  # Sender: 10 * 0.95 = 9.5
        social_res=SocialEngineeringResult(score=80.0),  # Social: 10 * 0.8 = 8.0
        attach_res=AttachmentAnalysisResult(score=100.0),  # Attach: 10 * 1.0 = 10.0
    )
    assert res.score >= 80.0
    assert res.severity == "CRITICAL"
    assert len(res.top_risk_contributors) >= 2


def test_content_anomalies_detection():
    """Verify zero-width space and hidden CSS styling are detected."""
    plain = "Hello team \u200b verify account"
    html = "<p style='display:none'>hidden instruction</p>"
    score, anomalies = evaluate_content_anomalies(plain, html)
    assert score >= 50.0
    assert any("Zero-width" in a for a in anomalies)
    assert any("hidden text" in a for a in anomalies)
