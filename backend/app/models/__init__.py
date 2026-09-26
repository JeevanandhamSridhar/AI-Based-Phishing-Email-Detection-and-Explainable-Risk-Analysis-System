"""SQLAlchemy Model Registry
"""

from app.core.database import Base
from app.models.analysis import AnalysisRecord
from app.models.metrics import ModelMetricRecord
from app.models.adversarial import AdversarialTestRecord

__all__ = [
    "Base",
    "AnalysisRecord",
    "ModelMetricRecord",
    "AdversarialTestRecord",
]
