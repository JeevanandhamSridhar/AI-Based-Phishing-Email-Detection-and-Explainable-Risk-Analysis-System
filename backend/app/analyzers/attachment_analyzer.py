"""Static Attachment Metadata Analyzer

Evaluates attachment risk purely from metadata (filename, extension, MIME type, SHA-256).
STRICT SAFETY INVARIANT: Attachments are NEVER executed, unpacked, or rendered.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.email import AttachmentMetadata

# Executable / Script extensions (immediate critical risk)
CRITICAL_EXTENSIONS = {
    ".exe", ".scr", ".bat", ".cmd", ".vbs", ".js", ".jse", ".wsf", ".wsh",
    ".ps1", ".jar", ".iso", ".img", ".vhd", ".hta", ".cpl", ".msi", ".msp", ".pif"
}

# Macro-enabled document extensions
MACRO_EXTENSIONS = {
    ".docm", ".xlsm", ".pptm", ".dotm", ".xltm", ".ppam", ".ppsm"
}

# Archive extensions commonly used to wrap malware
ARCHIVE_EXTENSIONS = {
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".img", ".cab"
}

# Known executable MIME types
EXECUTABLE_MIME_TYPES = {
    "application/x-msdownload",
    "application/x-executable",
    "application/x-dosexec",
    "application/x-sharedlib",
    "application/x-bat",
    "application/x-vbs",
    "application/x-sh",
}


class AnalyzedAttachment(BaseModel):
    filename: str
    extension: str
    double_extension: bool = False
    mime_type: str
    size_bytes: int
    sha256: str
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_category: str = "LOW"
    reasons: List[str] = Field(default_factory=list)


class AttachmentAnalysisResult(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Normalized composite attachment risk score (0-100)")
    total_attachments: int = 0
    high_risk_count: int = 0
    attachments: List[AnalyzedAttachment] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)


def analyze_single_attachment(att: AttachmentMetadata) -> AnalyzedAttachment:
    """Evaluates an individual attachment's metadata without executing."""
    reasons: List[str] = []
    ext = att.extension.lower()
    fname = att.filename.lower()
    mime = att.mime_type.lower()
    score = 0.0

    # 1. Double extension check
    if att.double_extension:
        score += 95.0
        reasons.append(f"Deceptive double-extension disguise detected: '{att.filename}'")

    # 2. Critical executable extension
    if ext in CRITICAL_EXTENSIONS:
        score = max(score, 90.0)
        reasons.append(f"High-risk executable/script extension ({ext})")

    # 3. Macro-enabled document extension
    elif ext in MACRO_EXTENSIONS:
        score = max(score, 75.0)
        reasons.append(f"Macro-enabled document format ({ext}) capable of arbitrary code execution")

    # 4. MIME-type discrepancy (e.g. extension says .pdf but MIME is executable)
    if mime in EXECUTABLE_MIME_TYPES:
        if ext not in CRITICAL_EXTENSIONS:
            score = max(score, 90.0)
            reasons.append(f"MIME type discrepancy: declared '{mime}' but extension is '{ext}'")

    # 5. Archive wrapper check
    if ext in ARCHIVE_EXTENSIONS and not att.double_extension:
        score = max(score, 35.0)
        reasons.append(f"Compressed archive container ({ext})")

    # Clean legitimate files (e.g. .pdf, .txt, .png, .docx without macros)
    if not reasons and ext in {".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".png", ".jpg", ".csv"}:
        score = 0.0

    final_score = min(100.0, max(0.0, score))
    category = "CRITICAL" if final_score >= 75.0 else ("HIGH" if final_score >= 50.0 else ("MODERATE" if final_score >= 25.0 else "LOW"))

    return AnalyzedAttachment(
        filename=att.filename,
        extension=att.extension,
        double_extension=att.double_extension,
        mime_type=att.mime_type,
        size_bytes=att.size_bytes,
        sha256=att.sha256,
        risk_score=round(final_score, 1),
        risk_category=category,
        reasons=reasons,
    )


def analyze_attachments(attachments: List[AttachmentMetadata]) -> AttachmentAnalysisResult:
    """Analyzes a list of attachments statically and computes composite attachment risk score."""
    if not attachments:
        return AttachmentAnalysisResult(
            score=0.0,
            total_attachments=0,
            high_risk_count=0,
            attachments=[],
            reasons=[],
        )

    analyzed_list: List[AnalyzedAttachment] = []
    overall_reasons: List[str] = []
    max_score = 0.0

    for a in attachments:
        item = analyze_single_attachment(a)
        analyzed_list.append(item)
        if item.risk_score > max_score:
            max_score = item.risk_score
        for r in item.reasons:
            if r not in overall_reasons:
                overall_reasons.append(r)

    high_risk = sum(1 for a in analyzed_list if a.risk_score >= 50.0)

    return AttachmentAnalysisResult(
        score=round(max_score, 1),
        total_attachments=len(attachments),
        high_risk_count=high_risk,
        attachments=analyzed_list,
        reasons=overall_reasons,
    )
