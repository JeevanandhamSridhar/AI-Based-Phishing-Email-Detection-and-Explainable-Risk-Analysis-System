"""Unit Tests for Header & Authentication Analyzer
"""

import pytest
from app.schemas.email import HeaderInfo
from app.analyzers.header_analyzer import analyze_headers, check_display_name_spoofing


def test_clean_authenticated_headers():
    """Verify clean email with verified SPF/DKIM receives near-zero risk score."""
    headers = HeaderInfo(
        from_header="PayPal Support <service@paypal.com>",
        sender_name="PayPal Support",
        sender_email="service@paypal.com",
        sender_domain="paypal.com",
        to_header="user@target.com",
        subject="Monthly Statement Available",
        authentication_results="mx.google.com; dkim=pass header.i=@paypal.com; spf=pass (google.com: domain of service@paypal.com designates 173.0.84.1 as permitted sender)",
        received_spf="Pass (mailfrom) identity=mailfrom; client-ip=173.0.84.1",
        reply_to="service@paypal.com",
        reply_to_domain="paypal.com",
    )

    result = analyze_headers(headers)
    assert result.score <= 10.0
    assert result.spf_status == "pass"
    assert result.dkim_status == "pass"
    assert result.reply_to_mismatch is False
    assert result.display_name_spoofing is False


def test_failed_spf_and_dmarc_headers():
    """Verify failed SPF and DMARC results in elevated risk score."""
    headers = HeaderInfo(
        from_header="Admin <admin@spoofed-bank.com>",
        sender_domain="spoofed-bank.com",
        authentication_results="spf=fail (sender IP unauthorized); dmarc=fail action=reject",
    )

    result = analyze_headers(headers)
    assert result.score >= 50.0
    assert result.spf_status == "fail"
    assert result.dmarc_status == "fail"
    assert any("SPF verification failed" in a for a in result.anomalies)


def test_reply_to_mismatch():
    """Verify discrepancy between From domain and Reply-To domain is flagged."""
    headers = HeaderInfo(
        from_header="Apple Security <support@apple.com>",
        sender_name="Apple Security",
        sender_domain="apple.com",
        reply_to="attacker-inbox@phishing-drop.ru",
        reply_to_domain="phishing-drop.ru",
    )

    result = analyze_headers(headers)
    assert result.reply_to_mismatch is True
    assert any("Reply-To domain mismatch" in a for a in result.anomalies)


def test_display_name_impersonation():
    """Verify display name spoofing is detected when claiming a major brand from an unrelated domain."""
    is_spoofed, brand = check_display_name_spoofing(
        display_name="Microsoft Account Team",
        sender_domain="random-cloud-host.xyz",
    )
    assert is_spoofed is True
    assert brand == "Microsoft"

    # Legitimate sender matching domain should NOT be flagged
    is_spoofed, brand = check_display_name_spoofing(
        display_name="Microsoft Account Team",
        sender_domain="account.microsoft.com",
    )
    assert is_spoofed is False
    assert brand is None


def test_full_header_analysis_display_spoofing():
    """Verify end-to-end header analysis flags display name impersonation."""
    headers = HeaderInfo(
        from_header="Netflix Billing <account@cheap-vps-server.net>",
        sender_name="Netflix Billing",
        sender_email="account@cheap-vps-server.net",
        sender_domain="cheap-vps-server.net",
        subject="Payment Declined",
    )

    result = analyze_headers(headers)
    assert result.display_name_spoofing is True
    assert result.spoofed_brand_detected == "Netflix"
    assert result.score >= 40.0
