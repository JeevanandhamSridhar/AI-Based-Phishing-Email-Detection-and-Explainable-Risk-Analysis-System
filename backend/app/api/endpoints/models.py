"""Model Performance & Experimental Telemetry Endpoints

Exposes genuine evaluation metrics for the ML baseline, Module A (AI Authorship cross-generator),
and Module B (Adversarial self-evaluation).
"""

from typing import Dict
from fastapi import APIRouter, status
from app.ml.prediction_service import ml_service
from app.authorship.classifier import authorship_service
from app.adversarial.evaluator import adversarial_evaluator

router = APIRouter(tags=["Model Evaluation & Telemetry"])


@router.get("/models/performance", status_code=status.HTTP_200_OK)
async def get_model_performance() -> Dict:
    """Returns authentic validation metrics for the baseline TF-IDF + Logistic Regression classifier."""
    metrics = ml_service.get_metrics()
    metadata = ml_service.get_model_metadata()

    return {
        "status": "ready" if ml_service.is_ready else "uninitialized",
        "model_name": "TF-IDF + Logistic Regression Baseline",
        "metadata": metadata,
        "evaluation": metrics,
    }


@router.get("/authorship/evaluate", status_code=status.HTTP_200_OK)
async def get_authorship_evaluation() -> Dict:
    """Returns Module A in-generator and cross-generator evaluation metrics and generalization drop."""
    metrics = authorship_service.get_evaluation_metrics()
    return {
        "module": "Module A: AI-Generated Phishing Indicator",
        "status": "ready" if authorship_service.is_ready else "uninitialized",
        "metrics": metrics,
        "caveat": "Model-based indicator, not proof of AI authorship.",
    }


@router.get("/adversarial/evaluate", status_code=status.HTTP_200_OK)
async def get_adversarial_evaluation() -> Dict:
    """Returns Module B explanation-guided adversarial self-evaluation results and evasion rates."""
    summary = adversarial_evaluator.run_evaluation()
    return {
        "module": "Module B: Explanation-Guided Adversarial Self-Evaluation",
        "results": summary.model_dump(),
        "academic_note": (
            "Tests model brittleness against SHAP-guided paraphrasing. "
            "Reported transparently as a system limitation."
        ),
    }
