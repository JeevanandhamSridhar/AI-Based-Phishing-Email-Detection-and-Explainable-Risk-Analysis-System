"""Unit Tests for Social-Engineering Rule-Based Analyzer
"""

import pytest
from app.analyzers.social_engineering_analyzer import analyze_social_engineering


def test_benign_business_email():
    """Verify normal business email contains zero social engineering triggers."""
    subject = "Quarterly Architecture Review Meeting"
    body = (
        "Hi Team,\n"
        "Attached is the agenda for our quarterly architecture review on Thursday.\n"
        "Please review the design document prior to the discussion.\n"
        "Best regards,\nEngineering Team"
    )
    res = analyze_social_engineering(subject, body)
    assert res.score == 0.0
    assert len(res.categories_flagged) == 0
    assert res.total_triggers_count == 0


def test_urgency_and_credential_harvesting_triad():
    """Verify acute urgency combined with credential verification is flagged with high risk."""
    subject = "URGENT: Final Notice - Immediate Action Required"
    body = (
        "Dear Customer,\n"
        "Your account suspended due to unauthorized activity.\n"
        "You must act now within 24 hours to restore access.\n"
        "Click here to login and verify your account credentials immediately.\n"
    )
    res = analyze_social_engineering(subject, body)
    assert res.score >= 70.0
    assert "urgency" in res.categories_flagged
    assert "credential_harvesting" in res.categories_flagged
    assert "threat_fear" in res.categories_flagged
    assert any("Coercive Triad" in r for r in res.reasons)


def test_financial_bait_and_extortion():
    """Verify financial bait triggers are identified."""
    subject = "Notification of Unclaimed Funds"
    body = "You have an unclaimed prize of 5 million dollars awaiting wire transfer refund."
    res = analyze_social_engineering(subject, body)
    assert "financial_bait" in res.categories_flagged
    assert res.score >= 20.0


def test_authority_it_pretext():
    """Verify IT administrator impersonation patterns are caught."""
    subject = "Mandatory Security Update from IT Helpdesk"
    body = "System administrator requires you to validate access credentials."
    res = analyze_social_engineering(subject, body)
    assert "authority_impersonation" in res.categories_flagged
    assert res.score >= 15.0
