"""Forensic Report Download Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.analysis import AnalysisRecord
from app.reports.pdf_generator import generate_forensic_pdf

router = APIRouter(prefix="/reports", tags=["Forensic Reports"])


@router.get("/download/{analysis_id}")
async def download_forensic_pdf(
    analysis_id: str,
    db: Session = Depends(get_db),
):
    """Generates and streams a forensic PDF security report for the requested investigation."""
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation record with ID '{analysis_id}' not found.",
        )

    # Reconstruct data dict for PDF generator
    analysis_data = {
        "id": record.id,
        "timestamp": record.created_at.isoformat(),
        "email_metadata": {
            "subject": record.subject,
            "from_header": record.sender,
            "sender_domain": record.sender_domain,
            "to_header": record.recipient,
            "sha256": record.raw_sha256,
        },
        "overall_risk": {
            "score": record.risk_score,
            "severity": record.severity,
        },
        "factor_breakdown": record.factor_breakdown or {},
        "explainability": {
            "human_readable_summary": record.plain_explanation,
            "caveat": "Model-based feature attribution, not definitive legal proof.",
        },
        "ai_authorship": {
            "ai_generated_likelihood": record.ai_generated_likelihood,
            "classification": record.ai_authorship_classification,
            "caveat": "Model-based indicator, not proof of AI authorship.",
        },
    }

    try:
        pdf_bytes = generate_forensic_pdf(analysis_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Forensic_Report_{analysis_id[:8]}.pdf"
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(exc)}",
        )
