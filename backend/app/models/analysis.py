"""SQLAlchemy Model for Email Analysis Forensics Records
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from app.core.database import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    file_name = Column(String(255), nullable=True)

    # Email Metadata
    subject = Column(String(500), nullable=False, default="(No Subject)")
    sender = Column(String(255), nullable=False, default="")
    sender_domain = Column(String(255), nullable=False, default="")
    recipient = Column(String(255), nullable=False, default="")
    raw_sha256 = Column(String(64), nullable=False, index=True)

    # Core Risk Outcomes
    risk_score = Column(Float, nullable=False, default=0.0)
    severity = Column(String(20), nullable=False, default="LOW")
    ml_probability = Column(Float, nullable=False, default=0.0)

    # Detailed Forensic Payloads
    factor_breakdown = Column(JSON, nullable=False, default=dict)
    url_findings = Column(JSON, nullable=False, default=list)
    header_findings = Column(JSON, nullable=False, default=dict)
    attachment_findings = Column(JSON, nullable=False, default=list)
    social_findings = Column(JSON, nullable=False, default=dict)

    # Explainability & AI Authorship
    plain_explanation = Column(Text, nullable=False, default="")
    shap_features = Column(JSON, nullable=False, default=dict)
    ai_generated_likelihood = Column(Float, nullable=False, default=0.0)
    ai_authorship_classification = Column(String(50), nullable=False, default="Unknown")

    # Raw Artifacts (for audit trail)
    raw_headers = Column(Text, nullable=True)
