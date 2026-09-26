"""Multi-Factor Hybrid Risk Engine

Fuses seven independent analytical signals using configurable weights into a composite
0–100 risk score and categorizes severity according to project-defined thresholds.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.core.config import settings
from app.analyzers.header_analyzer import HeaderAnalysisResult
from app.analyzers.url_analyzer import URLAnalysisResult
from app.analyzers.sender_analyzer import SenderAnalysisResult
from app.analyzers.social_engineering_analyzer import SocialEngineeringResult
from app.analyzers.attachment_analyzer import AttachmentAnalysisResult


class FactorScoreItem(BaseModel):
    weight: float
    raw_score: float = Field(..., ge=0.0, le=100.0)
    weighted_contribution: float
    details: Dict = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Overall risk score (0-100)")
    severity: str = Field(..., description="Categorical risk tier: LOW, MODERATE, HIGH, CRITICAL")
    threshold_bracket: str
    factor_breakdown: Dict[str, FactorScoreItem] = Field(default_factory=dict)
    top_risk_contributors: List[str] = Field(default_factory=list)


def evaluate_content_anomalies(body_plain: str, body_html: str) -> tuple[float, List[str]]:
    """Inspects text and HTML for structural obfuscation, zero-width chars, and hidden elements."""
    anomalies: List[str] = []
    score = 0.0

    # 1. Zero-width and invisible unicode characters
    zero_width_chars = ["\u200b", "\u200c", "\u200d", "\ufeff", "\u2060"]
    for zw in zero_width_chars:
        if zw in body_plain or zw in body_html:
            score += 35.0
            anomalies.append("Zero-width hidden unicode characters detected in message body")
            break

    # 2. Massive whitespace padding (common evasion trick pushing text below scroll window)
    if " \n \n \n" in body_plain or "\n\n\n\n\n\n" in body_plain:
        score += 20.0
        anomalies.append("Excessive vertical whitespace padding detected")

    # 3. Hidden styling markers in HTML
    if body_html:
        lower_html = body_html.lower()
        if "display:none" in lower_html or "visibility:hidden" in lower_html or "font-size:0" in lower_html:
            score += 30.0
            anomalies.append("CSS-concealed hidden text detected (display:none or zero font-size)")

    final_score = min(100.0, max(0.0, score))
    return final_score, anomalies


class RiskEngine:
    """Computes weighted multi-factor risk scores from analytical outputs."""

    def __init__(self):
        self.w_ml = settings.WEIGHT_ML_PHISHING
        self.w_url = settings.WEIGHT_URL_RISK
        self.w_header = settings.WEIGHT_HEADER_AUTH
        self.w_sender = settings.WEIGHT_SENDER_DOMAIN
        self.w_social = settings.WEIGHT_SOCIAL_ENG
        self.w_attach = settings.WEIGHT_ATTACHMENT
        self.w_content = settings.WEIGHT_CONTENT

    def classify_severity(self, score: float) -> tuple[str, str]:
        """Maps a 0-100 numerical score to project-defined severity tiers."""
        if score < settings.THRESHOLD_LOW:
            return "LOW", "0-24"
        elif score < settings.THRESHOLD_MODERATE:
            return "MODERATE", "25-49"
        elif score < settings.THRESHOLD_HIGH:
            return "HIGH", "50-74"
        else:
            return "CRITICAL", "75-100"

    def compute_risk(
        self,
        ml_prob: float,
        url_res: Optional[URLAnalysisResult] = None,
        header_res: Optional[HeaderAnalysisResult] = None,
        sender_res: Optional[SenderAnalysisResult] = None,
        social_res: Optional[SocialEngineeringResult] = None,
        attach_res: Optional[AttachmentAnalysisResult] = None,
        body_plain: str = "",
        body_html: str = "",
    ) -> RiskAssessment:
        """Aggregates all components into an explainable 100-point composite score."""
        # 1. Normalize individual raw scores (0-100 scale)
        ml_raw = min(100.0, max(0.0, ml_prob * 100.0))
        url_raw = url_res.score if url_res else 0.0
        header_raw = header_res.score if header_res else 0.0
        sender_raw = sender_res.score if sender_res else 0.0
        social_raw = social_res.score if social_res else 0.0
        attach_raw = attach_res.score if attach_res else 0.0

        content_raw, content_anomalies = evaluate_content_anomalies(body_plain, body_html)

        # 2. Calculate weighted contributions
        c_ml = (ml_raw / 100.0) * self.w_ml
        c_url = (url_raw / 100.0) * self.w_url
        c_header = (header_raw / 100.0) * self.w_header
        c_sender = (sender_raw / 100.0) * self.w_sender
        c_social = (social_raw / 100.0) * self.w_social
        c_attach = (attach_raw / 100.0) * self.w_attach
        c_content = (content_raw / 100.0) * self.w_content

        total_score = min(100.0, max(0.0, c_ml + c_url + c_header + c_sender + c_social + c_attach + c_content))
        total_score_rounded = round(total_score, 1)

        severity, bracket = self.classify_severity(total_score_rounded)

        factor_breakdown = {
            "ml_phishing": FactorScoreItem(
                weight=self.w_ml,
                raw_score=round(ml_raw, 1),
                weighted_contribution=round(c_ml, 2),
                details={"probability": round(ml_prob, 4)},
            ),
            "url_risk": FactorScoreItem(
                weight=self.w_url,
                raw_score=round(url_raw, 1),
                weighted_contribution=round(c_url, 2),
                details={"flagged_count": url_res.high_risk_count if url_res else 0},
            ),
            "header_auth": FactorScoreItem(
                weight=self.w_header,
                raw_score=round(header_raw, 1),
                weighted_contribution=round(c_header, 2),
                details={"spf": header_res.spf_status if header_res else "none"},
            ),
            "sender_domain": FactorScoreItem(
                weight=self.w_sender,
                raw_score=round(sender_raw, 1),
                weighted_contribution=round(c_sender, 2),
                details={"is_impersonation": sender_res.is_impersonation if sender_res else False},
            ),
            "social_engineering": FactorScoreItem(
                weight=self.w_social,
                raw_score=round(social_raw, 1),
                weighted_contribution=round(c_social, 2),
                details={"triggers": social_res.categories_flagged if social_res else []},
            ),
            "attachment_risk": FactorScoreItem(
                weight=self.w_attach,
                raw_score=round(attach_raw, 1),
                weighted_contribution=round(c_attach, 2),
                details={"total_attachments": attach_res.total_attachments if attach_res else 0},
            ),
            "content_anomalies": FactorScoreItem(
                weight=self.w_content,
                raw_score=round(content_raw, 1),
                weighted_contribution=round(c_content, 2),
                details={"anomalies": content_anomalies},
            ),
        }

        # Rank factors by weighted contribution
        ranked = sorted(
            factor_breakdown.items(),
            key=lambda item: item[1].weighted_contribution,
            reverse=True,
        )
        top_contributors = [k for k, v in ranked if v.weighted_contribution > 0.0][:3]

        return RiskAssessment(
            score=total_score_rounded,
            severity=severity,
            threshold_bracket=bracket,
            factor_breakdown=factor_breakdown,
            top_risk_contributors=top_contributors,
        )


risk_engine = RiskEngine()
