"""Email Triage & Forensics Orchestration Service

Coordinates the complete analytical pipeline: static parsing, multi-vector analyzers,
ML probability estimation, XAI synthesis, AI authorship estimation, and database persistence.
"""

from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlalchemy.orm import Session

from app.schemas.analysis import (
    FullAnalysisResponse,
    EmailMetadataSchema,
    OverallRiskSchema,
    ExplainabilitySchema,
    AIAuthorshipSchema,
)
from app.utils.email_parser import parse_email
from app.analyzers.header_analyzer import analyze_headers
from app.analyzers.url_analyzer import analyze_urls
from app.analyzers.sender_analyzer import analyze_sender
from app.analyzers.social_engineering_analyzer import analyze_social_engineering
from app.analyzers.attachment_analyzer import analyze_attachments
from app.ml.prediction_service import ml_service
from app.explainability.explainer import explainability_service
from app.authorship.classifier import authorship_service
from app.services.risk_engine import risk_engine
from app.models.analysis import AnalysisRecord
from app.core.logging import logger


class TriageService:
    """Orchestrates end-to-end multi-signal email security triage."""

    def analyze_email(
        self,
        raw_email: str,
        file_name: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> FullAnalysisResponse:
        """Executes the entire static analysis pipeline and saves forensic record."""
        # 1. Parse Email (MIME / RFC-822 / Text)
        parsed = parse_email(raw_email, file_name=file_name)
        analysis_id = str(uuid.uuid4())
        timestamp_now = datetime.now(timezone.utc).isoformat()

        # 2. Multi-Signal Static Analysis
        header_res = analyze_headers(parsed.headers)
        url_res = analyze_urls(parsed.urls)
        sender_res = analyze_sender(parsed.headers.sender_domain, parsed.headers.from_header)
        social_res = analyze_social_engineering(parsed.headers.subject, parsed.body_plain)
        attach_res = analyze_attachments(parsed.attachments)

        # 3. Machine Learning Inference
        ml_prob = ml_service.predict_proba(parsed.body_plain)

        # 4. Explainable AI Feature Attribution & Synthesis
        xai_res = explainability_service.explain_text(parsed.body_plain, top_k=4)

        # 5. Module A: AI Authorship Stylometric Estimation
        authorship_res = authorship_service.predict_ai_likelihood(parsed.body_plain)

        # 6. Multi-Factor Risk Engine Fusion (0-100)
        risk_res = risk_engine.compute_risk(
            ml_prob=ml_prob,
            url_res=url_res,
            header_res=header_res,
            sender_res=sender_res,
            social_res=social_res,
            attach_res=attach_res,
            body_plain=parsed.body_plain,
            body_html=parsed.body_html,
        )

        # Prepare serializable breakdown
        factor_breakdown_dict = {
            k: v.model_dump() for k, v in risk_res.factor_breakdown.items()
        }

        # 7. Persist to Database if Session provided
        if db is not None:
            try:
                db_record = AnalysisRecord(
                    id=analysis_id,
                    file_name=file_name,
                    subject=parsed.headers.subject,
                    sender=parsed.headers.sender_email or parsed.headers.from_header,
                    sender_domain=parsed.headers.sender_domain,
                    recipient=parsed.headers.to_header,
                    raw_sha256=parsed.sha256,
                    risk_score=risk_res.score,
                    severity=risk_res.severity,
                    ml_probability=ml_prob,
                    factor_breakdown=factor_breakdown_dict,
                    url_findings=[u.model_dump() for u in url_res.flagged_urls],
                    header_findings=header_res.model_dump(),
                    attachment_findings=[a.model_dump() for a in attach_res.attachments],
                    social_findings=social_res.model_dump(),
                    plain_explanation=xai_res.human_readable_summary,
                    shap_features={
                        "top_phishing": [f.model_dump() for f in xai_res.top_phishing_features],
                        "top_legitimate": [f.model_dump() for f in xai_res.top_legitimate_features],
                    },
                    ai_generated_likelihood=authorship_res.ai_generated_likelihood,
                    ai_authorship_classification=authorship_res.classification,
                    raw_headers=str(parsed.headers.raw_headers),
                )
                db.add(db_record)
                db.commit()
                logger.info("Persisted analysis record %s [Score: %s (%s)]", analysis_id, risk_res.score, risk_res.severity)
            except Exception as exc:
                logger.error("Failed to persist analysis record to database: %s", exc)
                db.rollback()

        # 8. Assemble Full Response Payload
        return FullAnalysisResponse(
            id=analysis_id,
            timestamp=timestamp_now,
            email_metadata=EmailMetadataSchema(
                subject=parsed.headers.subject,
                from_header=parsed.headers.from_header,
                sender_domain=parsed.headers.sender_domain,
                reply_to=parsed.headers.reply_to,
                to_header=parsed.headers.to_header,
                date=parsed.headers.date,
                sha256=parsed.sha256,
                body_text=parsed.body_plain,
            ),
            overall_risk=OverallRiskSchema(
                score=risk_res.score,
                severity=risk_res.severity,
                threshold_bracket=risk_res.threshold_bracket,
            ),
            factor_breakdown=factor_breakdown_dict,
            explainability=ExplainabilitySchema(
                method=xai_res.method,
                human_readable_summary=xai_res.human_readable_summary,
                top_phishing_features=[f.model_dump() for f in xai_res.top_phishing_features],
                top_legitimate_features=[f.model_dump() for f in xai_res.top_legitimate_features],
                caveat=xai_res.caveat,
            ),
            ai_authorship=AIAuthorshipSchema(
                ai_generated_likelihood=authorship_res.ai_generated_likelihood,
                classification=authorship_res.classification,
                stylometric_indicators=authorship_res.stylometric_indicators,
                caveat=authorship_res.caveat,
            ),
            url_findings=[u.model_dump() for u in url_res.flagged_urls],
            header_findings=header_res.model_dump(),
            attachment_findings=[a.model_dump() for a in attach_res.attachments],
            social_findings=social_res.model_dump(),
        )


triage_service = TriageService()
