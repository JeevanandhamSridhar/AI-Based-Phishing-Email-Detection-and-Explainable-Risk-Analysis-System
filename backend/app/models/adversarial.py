"""SQLAlchemy Model for Adversarial Self-Evaluation Test Records
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from app.core.database import Base


class AdversarialTestRecord(Base):
    __tablename__ = "adversarial_test_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    test_case_name = Column(String(150), nullable=False)

    original_text = Column(Text, nullable=False)
    perturbed_text = Column(Text, nullable=False)
    removed_triggers = Column(JSON, nullable=False, default=list)

    # ML Classifier Outcome Shift
    original_ml_prob = Column(Float, nullable=False)
    perturbed_ml_prob = Column(Float, nullable=False)
    evaded_ml = Column(Boolean, nullable=False, default=False)

    # Multi-Factor Risk Outcome Shift
    original_risk_score = Column(Float, nullable=False)
    perturbed_risk_score = Column(Float, nullable=False)
    score_drop = Column(Float, nullable=False)
    evaded_composite = Column(Boolean, nullable=False, default=False)

    details = Column(JSON, nullable=False, default=dict)
