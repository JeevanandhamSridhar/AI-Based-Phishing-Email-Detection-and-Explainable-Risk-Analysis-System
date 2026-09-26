"""ML Baseline Prediction Service

Provides fast, deterministic phishing probability prediction using the trained
TF-IDF + Logistic Regression model with complete local auditing.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple
import joblib
from app.core.config import settings
from app.core.logging import logger
from app.core.errors import ModelNotLoadedError

REPO_DIR = Path(__file__).resolve().parent.parent.parent.parent
# Support both repository root and backend directory as working directory
if (REPO_DIR / "models" / "baseline").exists():
    MODEL_DIR = REPO_DIR / "models" / "baseline"
else:
    MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models" / "baseline"


class MLPredictionService:
    """Service wrapping the baseline TF-IDF and Logistic Regression model."""

    _instance: Optional["MLPredictionService"] = None

    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or MODEL_DIR
        self.model = None
        self.vectorizer = None
        self.metadata: Dict = {}
        self.metrics: Dict = {}
        self._is_loaded = False
        self.load_model()

    @classmethod
    def get_instance(cls) -> "MLPredictionService":
        """Singleton accessor for the prediction service."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self) -> bool:
        """Loads serialized model, vectorizer, and evaluation metrics from disk."""
        model_path = self.model_dir / "model.joblib"
        vectorizer_path = self.model_dir / "vectorizer.joblib"
        metadata_path = self.model_dir / "metadata.json"
        metrics_path = self.model_dir / "metrics.json"

        if not (model_path.exists() and vectorizer_path.exists()):
            logger.warning("ML baseline model artifacts not found at %s. Service will run in uninitialized state.", self.model_dir)
            self._is_loaded = False
            return False

        try:
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)

            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

            if metrics_path.exists():
                with open(metrics_path, "r", encoding="utf-8") as f:
                    self.metrics = json.load(f)

            self._is_loaded = True
            logger.info("Successfully loaded ML baseline model (vocab size: %d)", len(self.vectorizer.vocabulary_))
            return True
        except Exception as exc:
            logger.error("Failed to load ML baseline model artifacts: %s", exc)
            self._is_loaded = False
            return False

    @property
    def is_ready(self) -> bool:
        """Checks if model and vectorizer are loaded in memory."""
        return self._is_loaded and self.model is not None and self.vectorizer is not None

    def predict_proba(self, text: str) -> float:
        """Computes calibrated posterior probability of the text being phishing (0.0 to 1.0)."""
        if not self.is_ready:
            # Fallback heuristic probability if model not trained
            logger.warning("ML model not loaded, returning default baseline probability.")
            return 0.5

        if not text or not text.strip():
            return 0.0

        features = self.vectorizer.transform([text])
        proba = self.model.predict_proba(features)[0, 1]
        return float(round(proba, 4))

    def predict(self, text: str, threshold: float = 0.5) -> int:
        """Returns binary classification: 1 for Phishing, 0 for Legitimate."""
        proba = self.predict_proba(text)
        return 1 if proba >= threshold else 0

    def get_model_metadata(self) -> Dict:
        """Returns model hyperparameters and training configuration."""
        return self.metadata

    def get_metrics(self) -> Dict:
        """Returns authentic, non-fabricated evaluation metrics from held-out test split."""
        return self.metrics


ml_service = MLPredictionService.get_instance()
