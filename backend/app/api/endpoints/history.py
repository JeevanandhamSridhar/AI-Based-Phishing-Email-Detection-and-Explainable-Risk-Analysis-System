"""Investigation History Endpoints

Provides paginated access to previous triage assessments and detailed forensic logs.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.analysis import AnalysisRecord
from app.schemas.analysis import HistoryItemSchema, FullAnalysisResponse, EmailMetadataSchema, OverallRiskSchema, ExplainabilitySchema, AIAuthorshipSchema

router = APIRouter(prefix="/history", tags=["Investigation History"])


@router.get("", response_model=List[HistoryItemSchema])
async def list_investigation_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    severity: Optional[str] = Query(None, description="Filter by risk tier: LOW, MODERATE, HIGH, CRITICAL"),
    db: Session = Depends(get_db),
) -> List[HistoryItemSchema]:
    """Returns paginated history of email triage investigations."""
    query = db.query(AnalysisRecord)

    if severity:
        query = query.filter(AnalysisRecord.severity == severity.upper())

    records = (
        query.order_by(AnalysisRecord.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return [
        HistoryItemSchema(
            id=r.id,
            created_at=r.created_at.isoformat(),
            subject=r.subject,
            sender=r.sender,
            sender_domain=r.sender_domain,
            risk_score=r.risk_score,
            severity=r.severity,
            ai_generated_likelihood=r.ai_generated_likelihood,
            sha256=r.raw_sha256,
        )
        for r in records
    ]


@router.get("/{analysis_id}", response_model=FullAnalysisResponse)
async def get_investigation_detail(
    analysis_id: str,
    db: Session = Depends(get_db),
) -> FullAnalysisResponse:
    """Retrieves full forensic triage details for a specific investigation ID."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation record with ID '{analysis_id}' was not found.",
        )

    # Reconstruct FullAnalysisResponse from database record
    return FullAnalysisResponse(
        id=record.id,
        timestamp=record.created_at.isoformat(),
        email_metadata=EmailMetadataSchema(
            subject=record.subject,
            from_header=record.sender,
            sender_domain=record.sender_domain,
            to_header=record.recipient,
            date="",
            sha256=record.raw_sha256,
        ),
        overall_risk=OverallRiskSchema(
            score=record.risk_score,
            severity=record.severity,
            threshold_bracket="75-100" if record.severity == "CRITICAL" else ("50-74" if record.severity == "HIGH" else "25-49"),
        ),
        factor_breakdown=record.factor_breakdown or {},
        explainability=ExplainabilitySchema(
            method="SHAP (LinearExplainer)",
            human_readable_summary=record.plain_explanation,
            top_phishing_features=(record.shap_features or {}).get("top_phishing", []),
            top_legitimate_features=(record.shap_features or {}).get("top_legitimate", []),
            caveat="Model-based feature attribution, not definitive legal proof.",
        ),
        ai_authorship=AIAuthorshipSchema(
            ai_generated_likelihood=record.ai_generated_likelihood,
            classification=record.ai_authorship_classification,
            stylometric_indicators={},
            caveat="Model-based indicator, not proof of AI authorship.",
        ),
        url_findings=record.url_findings or [],
        header_findings=record.header_findings or {},
        attachment_findings=record.attachment_findings or [],
        social_findings=record.social_findings or {},
    )
