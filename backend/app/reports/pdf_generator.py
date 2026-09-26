"""Forensic PDF Security Report Generator

Generates cryptographically stamped, professional incident response PDF forensic reports
using ReportLab with zero third-party cloud dependencies.
"""

from io import BytesIO
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


def generate_forensic_pdf(analysis_data: Dict[str, Any]) -> bytes:
    """Generates an executive-ready forensic PDF investigation report as a byte buffer."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica-Bold",
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    caveat_style = ParagraphStyle(
        "CaveatNotice",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        fontName="Helvetica-Oblique",
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("FORENSIC EMAIL RISK ASSESSMENT REPORT", title_style))
    story.append(Paragraph("AI-Based Phishing Detection & Explainable Security Intelligence", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3b82f6"), spaceAfter=14))

    # 2. Case Identification Table
    meta = analysis_data.get("email_metadata", {})
    risk = analysis_data.get("overall_risk", {})
    severity = risk.get("severity", "LOW")

    sev_color = colors.HexColor("#ef4444") if severity in ("HIGH", "CRITICAL") else (
        colors.HexColor("#f59e0b") if severity == "MODERATE" else colors.HexColor("#10b981")
    )

    id_data = [
        [
            Paragraph("<b>Investigation ID:</b>", body_style),
            Paragraph(analysis_data.get("id", "N/A"), body_style),
            Paragraph("<b>Severity Tier:</b>", body_style),
            Paragraph(f"<b><font color='{sev_color.hexval()}'>{severity} ({risk.get('score', 0.0)}/100)</font></b>", body_style),
        ],
        [
            Paragraph("<b>Timestamp:</b>", body_style),
            Paragraph(analysis_data.get("timestamp", "N/A")[:19] + " UTC", body_style),
            Paragraph("<b>Subject:</b>", body_style),
            Paragraph(meta.get("subject", "(No Subject)")[:40], body_style),
        ],
        [
            Paragraph("<b>Sender:</b>", body_style),
            Paragraph(meta.get("from_header", "Unknown")[:40], body_style),
            Paragraph("<b>Recipient:</b>", body_style),
            Paragraph(meta.get("to_header", "Unknown")[:40], body_style),
        ],
        [
            Paragraph("<b>SHA-256 Digest:</b>", body_style),
            Paragraph(f"<font size=7>{meta.get('sha256', 'N/A')}</font>", body_style),
            Paragraph("<b>Sender Domain:</b>", body_style),
            Paragraph(meta.get("sender_domain", "N/A"), body_style),
        ],
    ]

    id_table = Table(id_data, colWidths=[100, 160, 90, 180])
    id_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(id_table)
    story.append(Spacer(1, 14))

    # 3. Multi-Factor Risk Score Breakdown Table
    story.append(Paragraph("1. Multi-Factor Risk Score Breakdown", section_heading))
    breakdown = analysis_data.get("factor_breakdown", {})

    breakdown_rows = [
        [
            Paragraph("<b>Analytical Vector</b>", body_style),
            Paragraph("<b>Weight</b>", body_style),
            Paragraph("<b>Raw Score</b>", body_style),
            Paragraph("<b>Contribution</b>", body_style),
        ]
    ]

    factor_names = {
        "ml_phishing": "ML Phishing Probability",
        "url_risk": "Static URL Risk Analysis",
        "header_auth": "Header & Authentication (SPF/DKIM)",
        "sender_domain": "Sender Impersonation / Typosquatting",
        "social_engineering": "Social-Engineering Linguistic Triggers",
        "attachment_risk": "Static Attachment Metadata",
        "content_anomalies": "Content Obfuscation / Anomalies",
    }

    total_contribution = 0.0
    for key, label in factor_names.items():
        item = breakdown.get(key, {})
        w = item.get("weight", 0)
        raw = item.get("raw_score", 0.0)
        contrib = item.get("weighted_contribution", 0.0)
        total_contribution += contrib
        breakdown_rows.append([
            Paragraph(label, body_style),
            Paragraph(f"{w}%", body_style),
            Paragraph(f"{raw:.1f}/100", body_style),
            Paragraph(f"<b>{contrib:.2f}</b>", body_style),
        ])

    breakdown_rows.append([
        Paragraph("<b>Total Scaled Risk Score</b>", body_style),
        Paragraph("<b>100%</b>", body_style),
        Paragraph("-", body_style),
        Paragraph(f"<b><font size=10 color='{sev_color.hexval()}'>{risk.get('score', total_contribution):.1f} / 100</font></b>", body_style),
    ])

    score_table = Table(breakdown_rows, colWidths=[240, 80, 100, 110])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("LINEBELOW", (0, -1), (-1, -1), 1.5, colors.HexColor("#0f172a")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # 4. Explainable AI (XAI) Synthesis
    story.append(Paragraph("2. Explainable AI Analysis (SHAP Feature Attribution)", section_heading))
    xai = analysis_data.get("explainability", {})
    summary_text = xai.get("human_readable_summary", "No explanation available.")
    story.append(Paragraph(f"<b>Model Rationale:</b> {summary_text}", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>Caveat: {xai.get('caveat', 'Local model attribution, not proof.')}</i>", caveat_style))
    story.append(Spacer(1, 14))

    # 5. Module A: AI Authorship Indicator
    story.append(Paragraph("3. AI-Generated Authorship Estimation (Module A)", section_heading))
    authorship = analysis_data.get("ai_authorship", {})
    ai_pct = authorship.get("ai_generated_likelihood", 0.0)
    ai_class = authorship.get("classification", "Unknown")

    author_data = [
        [
            Paragraph("<b>AI Authorship Likelihood:</b>", body_style),
            Paragraph(f"<b>{ai_pct:.1f}%</b> ({ai_class})", body_style),
            Paragraph("<b>Classification Method:</b>", body_style),
            Paragraph("18-Feature Stylometric Model", body_style),
        ]
    ]
    author_table = Table(author_data, colWidths=[150, 150, 110, 120])
    author_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(author_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>Caveat: {authorship.get('caveat', 'Model-based indicator, not proof.')}</i>", caveat_style))
    story.append(Spacer(1, 16))

    # 6. Forensic Evidence Signatures
    story.append(Paragraph("4. Forensic Evidence Stamp & Safety Chain", section_heading))
    audit_data = [
        [Paragraph("<b>Message Digest:</b>", body_style), Paragraph(f"<font size=7>{meta.get('sha256', 'N/A')}</font>", body_style)],
        [Paragraph("<b>Defensive Invariant:</b>", body_style), Paragraph("Zero execution of attachments; Zero network resolution of URLs.", body_style)],
        [Paragraph("<b>Compliance Standard:</b>", body_style), Paragraph("Local-First Security Assessment (B.Sc. Capstone Architecture)", body_style)],
    ]
    audit_table = Table(audit_data, colWidths=[140, 390])
    audit_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(audit_table)

    doc.build(story)
    return buffer.getvalue()
