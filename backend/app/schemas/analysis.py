"""API Analysis Response Schemas
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class EmailMetadataSchema(BaseModel):
    subject: str
    from_header: str
    sender_domain: str
    reply_to: Optional[str] = None
    to_header: str
    date: str
    sha256: str


class OverallRiskSchema(BaseModel):
    score: float
    severity: str
    threshold_bracket: str


class ExplainabilitySchema(BaseModel):
    method: str
    human_readable_summary: str
    top_phishing_features: List[Dict[str, Any]]
    top_legitimate_features: List[Dict[str, Any]]
    caveat: str


class AIAuthorshipSchema(BaseModel):
    ai_generated_likelihood: float
    classification: str
    stylometric_indicators: Dict[str, float]
    caveat: str


class FullAnalysisResponse(BaseModel):
    id: str
    timestamp: str
    email_metadata: EmailMetadataSchema
    overall_risk: OverallRiskSchema
    factor_breakdown: Dict[str, Any]
    explainability: ExplainabilitySchema
    ai_authorship: AIAuthorshipSchema
    url_findings: List[Dict[str, Any]]
    header_findings: Dict[str, Any]
    attachment_findings: List[Dict[str, Any]]
    social_findings: Dict[str, Any]


class HistoryItemSchema(BaseModel):
    id: str
    created_at: str
    subject: str
    sender: str
    sender_domain: str
    risk_score: float
    severity: str
    ai_generated_likelihood: float
    sha256: str
