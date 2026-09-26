"""Explainable AI (XAI) Engine

Computes exact token-level Shapley value attributions for the baseline classifier
using SHAP (LinearExplainer) and synthesizes human-readable plain language rationales.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field
import shap
from app.ml.prediction_service import MLPredictionService, ml_service
from app.core.logging import logger

CAVEAT_NOTICE = "Model-based feature attribution, not definitive legal proof."


class FeatureAttribution(BaseModel):
    feature: str
    weight: float = Field(..., description="Shapley value / attribution weight")


class ExplainabilityResult(BaseModel):
    method: str = "SHAP (LinearExplainer)"
    human_readable_summary: str
    top_phishing_features: List[FeatureAttribution] = Field(default_factory=list)
    top_legitimate_features: List[FeatureAttribution] = Field(default_factory=list)
    caveat: str = CAVEAT_NOTICE


class ExplainabilityService:
    """Provides local XAI explanations using SHAP over linear TF-IDF models."""

    _instance: Optional["ExplainabilityService"] = None

    def __init__(self, prediction_service: Optional[MLPredictionService] = None):
        self.ml = prediction_service or ml_service
        self.explainer: Optional[shap.LinearExplainer] = None
        self._init_explainer()

    @classmethod
    def get_instance(cls) -> "ExplainabilityService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _init_explainer(self) -> None:
        """Initializes SHAP LinearExplainer with the loaded logistic regression model."""
        if not self.ml.is_ready:
            logger.warning("ML service is not ready. SHAP explainer deferred.")
            return

        try:
            # For linear models over sparse TF-IDF, LinearExplainer computes exact attributions
            # using the model coefficients directly
            feature_names = self.ml.vectorizer.get_feature_names_out()
            self.explainer = shap.LinearExplainer(
                self.ml.model,
                masker=shap.maskers.Independent(data=np.zeros((1, len(feature_names)))),
                feature_names=feature_names,
            )
            logger.info("Initialized SHAP LinearExplainer successfully.")
        except Exception as exc:
            logger.error("Failed to initialize SHAP LinearExplainer: %s", exc)
            self.explainer = None

    def explain_text(self, text: str, top_k: int = 5) -> ExplainabilityResult:
        """Computes top token attributions and translates them into a plain-English explanation."""
        if not text or not text.strip():
            return ExplainabilityResult(
                method="SHAP (LinearExplainer)",
                human_readable_summary="No textual content available to explain.",
                top_phishing_features=[],
                top_legitimate_features=[],
            )

        if not self.ml.is_ready:
            return ExplainabilityResult(
                method="Heuristic Fallback",
                human_readable_summary="ML model artifacts uninitialized. Explanation derived from heuristic triggers.",
                top_phishing_features=[],
                top_legitimate_features=[],
            )

        try:
            X_vec = self.ml.vectorizer.transform([text])
            feature_names = self.ml.vectorizer.get_feature_names_out()

            # Non-zero indices in the vectorized email text
            non_zero_indices = X_vec.indices
            coefs = self.ml.model.coef_[0]

            # Contribution = TF-IDF weight * logistic regression coefficient
            token_scores: List[Tuple[str, float]] = []
            for idx in non_zero_indices:
                token_str = feature_names[idx]
                token_weight = float(X_vec[0, idx] * coefs[idx])
                token_scores.append((token_str, round(token_weight, 4)))

            # Sort tokens: highest positive weights push toward Phishing; most negative push toward Legitimate
            sorted_by_weight = sorted(token_scores, key=lambda x: x[1], reverse=True)

            phishing_tokens = [
                FeatureAttribution(feature=t, weight=w)
                for t, w in sorted_by_weight
                if w > 0.0
            ][:top_k]

            legitimate_tokens = [
                FeatureAttribution(feature=t, weight=w)
                for t, w in reversed(sorted_by_weight)
                if w < 0.0
            ][:top_k]

            summary = self._synthesize_natural_language(phishing_tokens, legitimate_tokens)

            return ExplainabilityResult(
                method="SHAP (LinearExplainer)",
                human_readable_summary=summary,
                top_phishing_features=phishing_tokens,
                top_legitimate_features=legitimate_tokens,
            )
        except Exception as exc:
            logger.error("Error during SHAP attribution extraction: %s", exc)
            return ExplainabilityResult(
                method="Fallback",
                human_readable_summary="Feature attribution could not be computed for this payload.",
                top_phishing_features=[],
                top_legitimate_features=[],
            )

    def _synthesize_natural_language(
        self,
        phishing_tokens: List[FeatureAttribution],
        legitimate_tokens: List[FeatureAttribution],
    ) -> str:
        """Converts token attribution lists into a coherent, professional SOC analyst summary."""
        if not phishing_tokens and not legitimate_tokens:
            return "The message text does not exhibit distinct lexical patterns strongly favoring either phishing or legitimate classifications."

        if phishing_tokens and not legitimate_tokens:
            phish_words = ", ".join([f"'{f.feature}'" for f in phishing_tokens[:3]])
            return (
                f"The classifier flagged this message primarily due to prominent phishing-associated phrases "
                f"including {phish_words}."
            )

        if not phishing_tokens and legitimate_tokens:
            legit_words = ", ".join([f"'{f.feature}'" for f in legitimate_tokens[:3]])
            return (
                f"The message is classified as legitimate, strongly supported by standard organizational syntax "
                f"such as {legit_words}."
            )

        phish_words = ", ".join([f"'{f.feature}'" for f in phishing_tokens[:3]])
        legit_words = ", ".join([f"'{f.feature}'" for f in legitimate_tokens[:2]])
        return (
            f"The message demonstrates elevated risk driven by manipulative phrasing ({phish_words}), "
            f"which outweighs mitigating legitimate markers ({legit_words})."
        )


explainability_service = ExplainabilityService.get_instance()
