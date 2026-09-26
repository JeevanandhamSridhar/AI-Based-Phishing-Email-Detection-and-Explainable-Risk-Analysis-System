"""SQLAlchemy Model for Machine Learning Model Evaluation Runs
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.core.database import Base


class ModelMetricRecord(Base):
    __tablename__ = "model_metric_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    model_name = Column(String(100), nullable=False, index=True)
    evaluation_type = Column(String(50), nullable=False, index=True)

    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=True)

    confusion_matrix = Column(JSON, nullable=False, default=dict)
    sample_count = Column(Integer, nullable=False, default=0)
    metadata_info = Column(JSON, nullable=False, default=dict)
