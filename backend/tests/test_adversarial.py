"""Unit Tests for Module B: Explanation-Guided Adversarial Self-Evaluation
"""

import pytest
from app.adversarial.evaluator import AdversarialEvaluator, ADVERSARIAL_TEST_CASES


@pytest.fixture
def evaluator():
    return AdversarialEvaluator()


def test_adversarial_test_cases_integrity():
    """Verify that adversarial test suite has at least 10 pairs with removed triggers."""
    assert len(ADVERSARIAL_TEST_CASES) >= 10
    for case in ADVERSARIAL_TEST_CASES:
        assert "original_text" in case
        assert "perturbed_text" in case
        assert len(case["removed_triggers"]) >= 2
        assert case["original_text"] != case["perturbed_text"]


def test_run_adversarial_evaluation(evaluator):
    """Verify adversarial evaluation measures real probability drops and evasion outcomes."""
    summary = evaluator.run_evaluation()

    assert summary.total_cases_tested == len(ADVERSARIAL_TEST_CASES)
    assert summary.ml_evasions_count + summary.ml_retained_count == summary.total_cases_tested
    assert 0.0 <= summary.ml_evasion_rate_pct <= 100.0

    # The mean probability of original phishing text must be significantly higher than perturbed text
    assert summary.mean_original_proba > summary.mean_perturbed_proba
    assert summary.mean_proba_drop > 0.0

    # Ensure all individual test cases have computed drops
    for res in summary.case_results:
        assert res.original_ml_proba >= 0.0
        assert res.perturbed_ml_proba >= 0.0
        assert len(res.removed_triggers) > 0
