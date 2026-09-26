"""Unit Tests for Static URL Risk Analyzer

Strict verification that analysis is static and correctly identifies lexical threat patterns.
"""

import pytest
from app.analyzers.url_analyzer import analyze_single_url, analyze_urls, calculate_shannon_entropy


def test_clean_legitimate_url():
    """Verify standard legitimate URL receives very low risk score."""
    res = analyze_single_url("https://www.microsoft.com/en-us/windows")
    assert res.risk_score <= 15.0
    assert res.is_ip_host is False
    assert res.is_punycode is False
    assert res.brand_in_subdomain is None
    assert res.suspicious_tld is False


def test_raw_ip_address_url():
    """Verify raw IP host is flagged as dangerous."""
    res = analyze_single_url("http://192.168.1.100/login/auth.php")
    assert res.is_ip_host is True
    assert res.risk_score >= 40.0
    assert any("Raw IP address" in r for r in res.reasons)


def test_brand_in_subdomain_and_suspicious_tld():
    """Verify brand embedded in subdomain of a suspicious TLD domain is flagged."""
    res = analyze_single_url("http://paypal.com.user-verify.xyz/update-billing")
    assert res.brand_in_subdomain == "paypal"
    assert res.suspicious_tld is True
    assert res.risk_score >= 65.0
    assert any("Target brand 'paypal' deceptively placed" in r for r in res.reasons)
    assert any("Suspicious top-level domain" in r for r in res.reasons)


def test_punycode_homograph_detection():
    """Verify punycode (xn--) internationalized domain is flagged."""
    res = analyze_single_url("http://xn--microsft-07a.com/login")
    assert res.is_punycode is True
    assert res.risk_score >= 35.0
    assert any("Punycode" in r for r in res.reasons)


def test_at_symbol_deception():
    """Verify @ user-info authority deception is flagged."""
    res = analyze_single_url("http://google.com@phishing-target-server.com/signin")
    assert res.at_symbol_deception is True
    assert res.risk_score >= 45.0
    assert any("Deceptive '@'" in r for r in res.reasons)


def test_excessive_subdomains():
    """Verify deeply nested subdomain structures are flagged."""
    res = analyze_single_url("http://login.verify.account.security.target.com/index.html")
    assert res.excessive_subdomains is True
    assert any("Excessive subdomain depth" in r for r in res.reasons)


def test_shannon_entropy():
    """Verify Shannon entropy calculation detects randomized token strings."""
    regular_text = "welcome-to-the-portal"
    random_text = "a9f83c1b7e2d4059abcf81"
    assert calculate_shannon_entropy(random_text) > calculate_shannon_entropy(regular_text)


def test_empty_and_composite_url_analysis():
    """Verify aggregation across multiple URLs."""
    empty_res = analyze_urls([])
    assert empty_res.score == 0.0
    assert empty_res.total_urls == 0

    urls = [
        "https://www.google.com",
        "http://192.168.1.1/login",
    ]
    comp_res = analyze_urls(urls)
    assert comp_res.total_urls == 2
    assert comp_res.high_risk_count >= 1
    assert comp_res.score >= 35.0
