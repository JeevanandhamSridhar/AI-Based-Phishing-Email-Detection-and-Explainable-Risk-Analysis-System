"""Unit Tests for Forensic PDF Report Generation
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.reports.pdf_generator import generate_forensic_pdf

client = TestClient(app)


def test_generate_forensic_pdf_bytes():
    """Verify that generate_forensic_pdf produces valid PDF binary output."""
    sample_data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2026-09-26T22:30:00Z",
        "email_metadata": {
            "subject": "Urgent Security Verification Notice",
            "from_header": "PayPal Support <security@paypa1.com>",
            "sender_domain": "paypa1.com",
            "to_header": "victim@example.com",
            "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        },
        "overall_risk": {
            "score": 88.5,
            "severity": "CRITICAL",
        },
        "factor_breakdown": {
            "ml_phishing": {"weight": 30, "raw_score": 95.0, "weighted_contribution": 28.5},
            "url_risk": {"weight": 20, "raw_score": 90.0, "weighted_contribution": 18.0},
            "header_auth": {"weight": 15, "raw_score": 80.0, "weighted_contribution": 12.0},
            "sender_domain": {"weight": 10, "raw_score": 90.0, "weighted_contribution": 9.0},
            "social_engineering": {"weight": 10, "raw_score": 85.0, "weighted_contribution": 8.5},
            "attachment_risk": {"weight": 10, "raw_score": 0.0, "weighted_contribution": 0.0},
            "content_anomalies": {"weight": 5, "raw_score": 0.0, "weighted_contribution": 0.0},
        },
        "explainability": {
            "human_readable_summary": "High risk detected due to urgent account verification combined with typosquatted sender domain.",
            "caveat": "Model-based feature attribution, not definitive legal proof.",
        },
        "ai_authorship": {
            "ai_generated_likelihood": 78.4,
            "classification": "Likely LLM-Generated",
            "caveat": "Model-based indicator, not proof of AI authorship.",
        },
    }

    pdf_bytes = generate_forensic_pdf(sample_data)
    assert len(pdf_bytes) > 1000
    # Standard PDF file header magic number
    assert pdf_bytes.startswith(b"%PDF-")


def test_download_report_endpoint():
    """Verify GET /api/reports/download/{id} streams valid PDF file."""
    # First analyze an email to get an ID in the DB
    raw = (
        "From: service@paypa1.com\n"
        "To: victim@example.com\n"
        "Subject: Urgent Account Verification\n\n"
        "Please verify your credentials at http://paypa1.com/login"
    )
    analyze_res = client.post("/api/analyze", json={"raw_email": raw})
    assert analyze_res.status_code == 200
    analysis_id = analyze_res.json()["id"]

    download_res = client.get(f"/api/reports/download/{analysis_id}")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/pdf"
    assert "attachment" in download_res.headers["content-disposition"]
    assert download_res.content.startswith(b"%PDF-")
