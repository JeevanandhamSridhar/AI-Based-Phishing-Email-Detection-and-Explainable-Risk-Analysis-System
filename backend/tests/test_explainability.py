"""Unit Tests for Explainable AI (XAI) Service
"""

import pytest
from app.explainability.explainer import ExplainabilityService, CAVEAT_NOTICE


@pytest.fixture
def explainer():
    """Provides an initialized explainability service."""
    return ExplainabilityService.get_instance()


def test_explain_phishing_text(explainer):
    """Verify explainability on phishing text extracts top trigger tokens."""
    phish_text = (
        "Urgent: Your account has been suspended due to unauthorized access. "
        "Verify your password and billing credentials immediately to prevent termination."
    )
    result = explainer.explain_text(phish_text, top_k=4)

    assert result.caveat == CAVEAT_NOTICE
    assert len(result.top_phishing_features) > 0
    assert len(result.human_readable_summary) > 20

    # Top phishing tokens should have positive weights
    for feat in result.top_phishing_features:
        assert feat.weight > 0.0

    # Check that summary mentions flagged phrases
    assert "flagged" in result.human_readable_summary.lower() or "elevated" in result.human_readable_summary.lower()


def test_explain_legitimate_text(explainer):
    """Verify explainability on legitimate text extracts legitimate-supporting tokens."""
    legit_text = (
        "Attached is the agenda for our team meeting on Friday. "
        "Please review the design document before our discussion."
    )
    result = explainer.explain_text(legit_text, top_k=4)

    assert result.caveat == CAVEAT_NOTICE
    assert len(result.human_readable_summary) > 20


def test_explain_empty_text(explainer):
    """Verify empty text edge case returns graceful response."""
    result = explainer.explain_text("")
    assert "No textual content" in result.human_readable_summary
    assert len(result.top_phishing_features) == 0
