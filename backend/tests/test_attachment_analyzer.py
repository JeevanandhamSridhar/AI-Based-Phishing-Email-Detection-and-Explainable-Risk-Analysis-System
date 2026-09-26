"""Unit Tests for Static Attachment Metadata Analyzer
"""

import pytest
from app.schemas.email import AttachmentMetadata
from app.analyzers.attachment_analyzer import analyze_single_attachment, analyze_attachments


def test_benign_pdf_attachment():
    """Verify clean document receives zero risk score."""
    att = AttachmentMetadata(
        filename="company_policy_2026.pdf",
        extension=".pdf",
        double_extension=False,
        mime_type="application/pdf",
        size_bytes=452000,
        sha256="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        is_executable=False,
        is_macro_enabled=False,
    )
    res = analyze_single_attachment(att)
    assert res.risk_score == 0.0
    assert res.risk_category == "LOW"
    assert len(res.reasons) == 0


def test_executable_attachment():
    """Verify executable extension triggers critical risk."""
    att = AttachmentMetadata(
        filename="update_patch.exe",
        extension=".exe",
        double_extension=False,
        mime_type="application/x-msdownload",
        size_bytes=1048576,
        sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        is_executable=True,
        is_macro_enabled=False,
    )
    res = analyze_single_attachment(att)
    assert res.risk_score >= 90.0
    assert res.risk_category == "CRITICAL"
    assert any("executable/script" in r for r in res.reasons)


def test_double_extension_disguise():
    """Verify deceptive double extensions receive maximum risk."""
    att = AttachmentMetadata(
        filename="Urgent_Invoice.pdf.exe",
        extension=".exe",
        double_extension=True,
        mime_type="application/x-msdownload",
        size_bytes=204800,
        sha256="aaaabbbbccccddddeeeeffff0000111122223333444455556666777788889999",
        is_executable=True,
        is_macro_enabled=False,
    )
    res = analyze_single_attachment(att)
    assert res.risk_score >= 95.0
    assert res.double_extension is True
    assert any("double-extension" in r for r in res.reasons)


def test_macro_enabled_office_document():
    """Verify macro-enabled files are flagged."""
    att = AttachmentMetadata(
        filename="budget_tracker.xlsm",
        extension=".xlsm",
        double_extension=False,
        mime_type="application/vnd.ms-excel.sheet.macroEnabled.12",
        size_bytes=350000,
        sha256="9999888877776666555544443333222211110000ffffeeeeddddccccbbbbaaaa",
        is_executable=False,
        is_macro_enabled=True,
    )
    res = analyze_single_attachment(att)
    assert res.risk_score >= 75.0
    assert any("Macro-enabled" in r for r in res.reasons)


def test_mime_type_discrepancy():
    """Verify disguised executable with innocent extension is flagged."""
    att = AttachmentMetadata(
        filename="report.pdf",
        extension=".pdf",
        double_extension=False,
        mime_type="application/x-msdownload",
        size_bytes=89000,
        sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        is_executable=False,
        is_macro_enabled=False,
    )
    res = analyze_single_attachment(att)
    assert res.risk_score >= 85.0
    assert any("MIME type discrepancy" in r for r in res.reasons)


def test_empty_and_composite_attachments():
    """Verify list aggregation across attachments."""
    empty_res = analyze_attachments([])
    assert empty_res.score == 0.0
    assert empty_res.total_attachments == 0

    att1 = AttachmentMetadata(
        filename="notes.txt",
        extension=".txt",
        double_extension=False,
        mime_type="text/plain",
        size_bytes=1024,
        sha256="abc1",
    )
    att2 = AttachmentMetadata(
        filename="setup.scr",
        extension=".scr",
        double_extension=False,
        mime_type="application/x-msdownload",
        size_bytes=50000,
        sha256="abc2",
        is_executable=True,
    )
    comp_res = analyze_attachments([att1, att2])
    assert comp_res.total_attachments == 2
    assert comp_res.high_risk_count == 1
    assert comp_res.score >= 90.0
