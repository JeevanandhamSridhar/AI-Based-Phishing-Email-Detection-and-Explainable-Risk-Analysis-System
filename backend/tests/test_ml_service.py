"""Unit Tests for ML Baseline Prediction Service
"""

import pytest
from app.ml.prediction_service import MLPredictionService


@pytest.fixture
def service():
    """Provides an initialized prediction service instance."""
    svc = MLPredictionService.get_instance()
    assert svc.is_ready is True
    return svc


def test_model_loaded_and_ready(service):
    """Verify that model and vectorizer are loaded in memory."""
    assert service.is_ready is True
    metadata = service.get_model_metadata()
    assert metadata["model_type"] == "LogisticRegression"
    assert metadata["vocabulary_size"] > 0

    metrics = service.get_metrics()
    assert "metrics" in metrics or "accuracy" in metrics


def test_predict_phishing_text(service):
    """Verify high phishing probability for clear phishing text."""
    phish_text = (
        "Urgent: Your PayPal account has been suspended due to unauthorized login attempts. "
        "Click here immediately to verify your password and update your billing credentials: "
        "http://paypal.com.verify-access.xyz/login"
    )
    proba = service.predict_proba(phish_text)
    pred = service.predict(phish_text)

    assert proba >= 0.70
    assert pred == 1


def test_predict_legitimate_text(service):
    """Verify low phishing probability for clear legitimate text."""
    legit_text = (
        "Hi team, attached is the revised roadmap for our microservices deployment on Friday. "
        "Please review the design document prior to our architecture review meeting in Room B."
    )
    proba = service.predict_proba(legit_text)
    pred = service.predict(legit_text)

    assert proba <= 0.35
    assert pred == 0


def test_empty_string_handling(service):
    """Verify empty or whitespace strings return zero probability without error."""
    assert service.predict_proba("") == 0.0
    assert service.predict_proba("    ") == 0.0
