"""Unit Tests for Static RFC-822 / MIME Email Parser
"""

import pytest
from app.utils.email_parser import parse_email, check_double_extension, extract_domain_from_email


def test_extract_domain_from_email():
    """Verify domain extraction from complex email headers."""
    assert extract_domain_from_email("PayPal Support <support@paypal.com>") == "paypal.com"
    assert extract_domain_from_email("attacker@sub.evil-domain.xyz") == "sub.evil-domain.xyz"
    assert extract_domain_from_email("plain-address@test.org") == "test.org"
    assert extract_domain_from_email("malformed-address") == ""


def test_check_double_extension():
    """Verify detection of dangerous double-extension files."""
    is_double, ext = check_double_extension("invoice.pdf.exe")
    assert is_double is True
    assert ext == ".exe"

    is_double, ext = check_double_extension("document.docx.vbs")
    assert is_double is True
    assert ext == ".vbs"

    is_double, ext = check_double_extension("legitimate_report.pdf")
    assert is_double is False
    assert ext == ".pdf"


def test_parse_plain_rfc822_email():
    """Verify parsing of standard plain-text RFC-822 email."""
    raw = (
        "From: IT Helpdesk <admin@company.com>\n"
        "To: employee@company.com\n"
        "Subject: Scheduled Server Maintenance\n"
        "Date: Sat, 26 Sep 2026 10:00:00 +0000\n"
        "Message-ID: <12345@company.com>\n"
        "\n"
        "Hello Team,\n"
        "Server maintenance is scheduled for tonight at 11 PM.\n"
        "Please visit https://portal.company.com/status for updates.\n"
    )

    parsed = parse_email(raw)
    assert parsed.headers.subject == "Scheduled Server Maintenance"
    assert parsed.headers.sender_email == "admin@company.com"
    assert parsed.headers.sender_domain == "company.com"
    assert parsed.headers.sender_name == "IT Helpdesk"
    assert parsed.headers.to_header == "employee@company.com"
    assert "Server maintenance is scheduled" in parsed.body_plain
    assert "https://portal.company.com/status" in parsed.urls
    assert len(parsed.sha256) == 64


def test_parse_multipart_html_email_with_links():
    """Verify HTML parsing and URL extraction from anchor tags."""
    raw = (
        "From: Alerts <service@paypa1.com>\n"
        "To: victim@example.com\n"
        "Subject: Urgent Action Required\n"
        "MIME-Version: 1.0\n"
        "Content-Type: multipart/alternative; boundary=\"boundary123\"\n"
        "\n"
        "--boundary123\n"
        "Content-Type: text/plain; charset=utf-8\n"
        "\n"
        "Your account is limited. Click here: http://192.168.1.50/login\n"
        "--boundary123\n"
        "Content-Type: text/html; charset=utf-8\n"
        "\n"
        "<html><body>\n"
        "<p>Your account is limited.</p>\n"
        "<a href=\"http://evil-verification-portal.com/update\">Click to Verify</a>\n"
        "</body></html>\n"
        "--boundary123--\n"
    )

    parsed = parse_email(raw)
    assert parsed.headers.subject == "Urgent Action Required"
    assert parsed.headers.sender_domain == "paypa1.com"
    assert "Your account is limited" in parsed.body_plain
    # Both URLs should be captured
    assert "http://192.168.1.50/login" in parsed.urls
    assert "http://evil-verification-portal.com/update" in parsed.urls


def test_parse_email_with_attachment_metadata():
    """Verify passive attachment metadata extraction (zero execution)."""
    raw = (
        "From: billing@vendor.com\n"
        "To: accounts@target.com\n"
        "Subject: Past Due Invoice\n"
        "MIME-Version: 1.0\n"
        "Content-Type: multipart/mixed; boundary=\"attach_boundary\"\n"
        "\n"
        "--attach_boundary\n"
        "Content-Type: text/plain\n"
        "\n"
        "Please find the invoice attached.\n"
        "--attach_boundary\n"
        "Content-Type: application/octet-stream; name=\"Invoice_2026.pdf.exe\"\n"
        "Content-Disposition: attachment; filename=\"Invoice_2026.pdf.exe\"\n"
        "Content-Transfer-Encoding: base64\n"
        "\n"
        "TVpQAAIAAAAA//8AALUiAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n"
        "--attach_boundary--\n"
    )

    parsed = parse_email(raw)
    assert len(parsed.attachments) == 1
    att = parsed.attachments[0]
    assert att.filename == "Invoice_2026.pdf.exe"
    assert att.extension == ".exe"
    assert att.double_extension is True
    assert att.is_executable is True
    assert att.size_bytes > 0
    assert len(att.sha256) == 64


def test_parse_unstructured_pasted_text():
    """Verify fallback handling for plain pasted text without formal headers."""
    raw = "Urgent: Your bank account has been locked. Verify immediately at http://secure-bank-update.xyz"
    parsed = parse_email(raw)
    assert "Urgent: Your bank account" in parsed.body_plain
    assert "http://secure-bank-update.xyz" in parsed.urls
    assert len(parsed.sha256) == 64
