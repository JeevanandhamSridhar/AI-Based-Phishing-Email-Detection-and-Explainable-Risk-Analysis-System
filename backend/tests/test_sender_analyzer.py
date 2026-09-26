"""Unit Tests for Sender & Domain Impersonation Analyzer
"""

import pytest
from app.analyzers.sender_analyzer import (
    analyze_sender,
    evaluate_domain_typosquatting,
    detect_unicode_homoglyphs,
)


def test_legitimate_brand_domains():
    """Verify official legitimate domains are recognized and receive zero risk score."""
    res = analyze_sender("paypal.com")
    assert res.is_impersonation is False
    assert res.score == 0.0

    res_sub = analyze_sender("mail.microsoft.com")
    assert res_sub.is_impersonation is False
    assert res_sub.score == 0.0


def test_typosquatted_domains_distance_one():
    """Verify single-character distance typosquats are caught."""
    res = analyze_sender("paypa1.com")
    assert res.is_impersonation is True
    assert res.impersonated_brand == "Paypal"
    assert res.score >= 80.0
    assert any("Levenshtein" in r or "Homoglyph" in r for r in res.reasons)

    res_ms = analyze_sender("micros0ft.com")
    assert res_ms.is_impersonation is True
    assert res_ms.impersonated_brand == "Microsoft"
    assert res_ms.score >= 80.0


def test_brand_token_insertion():
    """Verify deceptive insertion of brand names with hyphens is caught."""
    res = analyze_sender("paypal-security-alert.com")
    assert res.is_impersonation is True
    assert res.impersonated_brand == "Paypal"
    assert res.score >= 70.0
    assert any("Brand token insertion" in r for r in res.reasons)


def test_unicode_homoglyphs():
    """Verify detection of Cyrillic lookalike characters in domain strings."""
    # 'pаypal.com' using Cyrillic 'а' (\u0430)
    cyrillic_domain = "p\u0430ypal.com"
    is_homo, detected, norm = detect_unicode_homoglyphs(cyrillic_domain)
    assert is_homo is True
    assert len(detected) >= 1

    res = analyze_sender(cyrillic_domain)
    assert res.score >= 70.0
    assert len(res.homoglyphs_detected) >= 1


def test_neutral_unrelated_domain():
    """Verify normal benign business domains are not flagged."""
    res = analyze_sender("acme-consulting-services.com")
    assert res.is_impersonation is False
    assert res.score == 0.0
