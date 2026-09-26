"""Unit Tests for Module A: AI Authorship Stylometric Classifier
"""

import pytest
from app.authorship.stylometry import extract_stylometric_features, FEATURE_NAMES
from app.authorship.classifier import AIAuthorshipService, AUTHORSHIP_CAVEAT


@pytest.fixture
def service():
    svc = AIAuthorshipService.get_instance()
    assert svc.is_ready is True
    return svc


def test_stylometric_feature_extraction():
    """Verify feature extractor computes 18-dimensional vector and dictionary."""
    sample_text = (
        "Furthermore, in accordance with regulatory compliance, please verify your credentials. "
        "Additionally, your session will expire shortly."
    )
    vec, feat_dict = extract_stylometric_features(sample_text)

    assert len(vec) == 18
    assert len(feat_dict) == 18
    assert feat_dict["formal_connective_density"] > 0.0
    assert feat_dict["avg_sentence_length"] > 0.0
    assert 0.0 <= feat_dict["type_token_ratio"] <= 1.0


def test_predict_llm_generated_style(service):
    """Verify formal, uniform LLM writing style yields elevated AI likelihood."""
    llm_sample = (
        "Dear Valued Customer, We have detected anomalous sign-in activity regarding your corporate account credentials. "
        "Consequently, we have temporarily restricted access in order to preserve security integrity. "
        "Please review your recent activity and verify your authentication profile at our portal. "
        "We appreciate your immediate cooperation. Sincerely, Risk Management Operations."
    )
    res = service.predict_ai_likelihood(llm_sample)
    assert res.ai_generated_likelihood >= 50.0
    assert res.classification == "Likely LLM-Generated"
    assert res.caveat == AUTHORSHIP_CAVEAT
    assert "formal_connective_density" in res.stylometric_indicators


def test_predict_human_written_style(service):
    """Verify informal, erratic human phrasing yields lower AI likelihood."""
    human_sample = (
        "DEAR CUSTOMER!! URGENT!! Ur account has been suspended! Clickk here ASAP: "
        "http://paypa1-update.xyz to confirm ur password or account will be DELETED forever!!"
    )
    res = service.predict_ai_likelihood(human_sample)
    assert res.ai_generated_likelihood <= 50.0
    assert res.classification == "Likely Human-Written"
    assert res.caveat == AUTHORSHIP_CAVEAT


def test_cross_generator_metrics_availability(service):
    """Verify authentic cross-generator evaluation metrics are populated and report drop."""
    metrics = service.get_evaluation_metrics()
    assert "in_generator_metrics" in metrics
    assert "cross_generator_metrics" in metrics

    cr_m = metrics["cross_generator_metrics"]
    assert "performance_drop_delta_f1" in cr_m
    assert cr_m["performance_drop_delta_f1"] is not None


def test_empty_text_authorship(service):
    """Verify empty text edge case."""
    res = service.predict_ai_likelihood("")
    assert res.ai_generated_likelihood == 0.0
    assert res.classification == "Insufficient Text"
