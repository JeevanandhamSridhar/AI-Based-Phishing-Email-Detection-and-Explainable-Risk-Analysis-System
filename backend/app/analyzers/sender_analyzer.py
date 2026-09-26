"""Sender & Domain Impersonation Analyzer

Detects typosquatting, lookalike homoglyphs, and brand name impersonation
in sender email domains using Levenshtein distance and phonetic/visual heuristics.
"""

import re
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
import Levenshtein
import tldextract

# Reference dictionary of primary target brands and their official base domains
TARGET_BRAND_DOMAINS = {
    "paypal": "paypal.com",
    "microsoft": "microsoft.com",
    "apple": "apple.com",
    "google": "google.com",
    "amazon": "amazon.com",
    "netflix": "netflix.com",
    "chase": "chase.com",
    "wellsfargo": "wellsfargo.com",
    "bankofamerica": "bankofamerica.com",
    "docusign": "docusign.com",
    "dropbox": "dropbox.com",
    "meta": "meta.com",
    "facebook": "facebook.com",
    "instagram": "instagram.com",
    "linkedin": "linkedin.com",
    "coinbase": "coinbase.com",
    "binance": "binance.com",
    "dhl": "dhl.com",
    "fedex": "fedex.com",
    "ups": "ups.com",
    "irs": "irs.gov",
}

# Homoglyph lookup map (common Cyrillic and symbol characters mimicking Latin)
HOMOGLYPH_MAP = {
    "а": "a", "с": "c", "е": "e", "о": "o", "р": "p", "х": "x", "у": "y",
    "і": "i", "ј": "j", "ѕ": "s", "ԁ": "d", "ԛ": "q", "0": "o", "1": "l",
    "5": "s", "8": "b",
}


class SenderAnalysisResult(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Normalized sender impersonation risk score (0-100)")
    sender_domain: str = ""
    is_impersonation: bool = False
    impersonated_brand: Optional[str] = None
    target_domain: Optional[str] = None
    typosquat_pattern: Optional[str] = None
    homoglyphs_detected: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)


def detect_unicode_homoglyphs(domain: str) -> Tuple[bool, List[str], str]:
    """Detects mixed-script or lookalike homoglyphs and produces normalized Latin equivalent."""
    detected = []
    normalized_chars = []
    for char in domain:
        if char in HOMOGLYPH_MAP:
            detected.append(f"'{char}' -> '{HOMOGLYPH_MAP[char]}'")
            normalized_chars.append(HOMOGLYPH_MAP[char])
        else:
            normalized_chars.append(char)
    is_homoglyph = len(detected) > 0
    return is_homoglyph, detected, "".join(normalized_chars)


def evaluate_domain_typosquatting(sender_domain: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str], float]:
    """Evaluates whether sender domain is a typosquatted variant of a known target brand."""
    if not sender_domain:
        return False, None, None, None, 0.0

    ext = tldextract.extract(sender_domain)
    sld = ext.domain.lower()  # second-level domain (e.g. 'paypa1')
    full_dom = f"{sld}.{ext.suffix}".lower()

    # Exact legitimate match check
    for brand, legit_dom in TARGET_BRAND_DOMAINS.items():
        if full_dom == legit_dom or full_dom.endswith("." + legit_dom):
            return False, None, None, None, 0.0

    # 1. Check for homoglyphs in SLD
    is_homo, homo_list, normalized_sld = detect_unicode_homoglyphs(sld)

    for brand, legit_dom in TARGET_BRAND_DOMAINS.items():
        legit_sld = brand.lower()

        # Check Levenshtein distance on raw and normalized SLD
        raw_dist = Levenshtein.distance(sld, legit_sld)
        norm_dist = Levenshtein.distance(normalized_sld, legit_sld)

        # Direct homoglyph brand impersonation (e.g. 'paypa1' -> 'paypal')
        if norm_dist == 0 and sld != legit_sld:
            pattern = f"Homoglyph brand spoof: '{sld}' normalizes directly to target brand '{legit_sld}'"
            return True, brand.title(), legit_dom, pattern, 95.0

        # Immediate typosquat match: distance of 1 or 2 on brands with length >= 4
        min_dist = min(raw_dist, norm_dist)
        if len(legit_sld) >= 4 and min_dist in (1, 2) and sld != legit_sld:
            pattern = f"Typosquat: '{sld}' resembles '{legit_sld}' (Levenshtein distance: {min_dist})"
            risk = 90.0 if min_dist == 1 else 75.0
            return True, brand.title(), legit_dom, pattern, risk

        # Substring impersonation with deceptive hyphens (e.g. 'paypal-security')
        if legit_sld in sld and sld != legit_sld:
            pattern = f"Brand token insertion: '{legit_sld}' embedded within unregistered domain '{sld}'"
            return True, brand.title(), legit_dom, pattern, 80.0

    return False, None, None, None, 0.0


def analyze_sender(sender_domain: str, from_header: str = "") -> SenderAnalysisResult:
    """Performs static impersonation and typosquatting analysis on the sender domain."""
    reasons: List[str] = []
    clean_domain = sender_domain.lower().strip()

    if not clean_domain:
        return SenderAnalysisResult(
            score=25.0,
            sender_domain="",
            is_impersonation=False,
            reasons=["Missing sender domain in email headers"],
        )

    is_impersonated, brand, target_dom, pattern, score = evaluate_domain_typosquatting(clean_domain)
    is_homo, homo_chars, _ = detect_unicode_homoglyphs(clean_domain)

    if is_impersonated:
        reasons.append(pattern)
        if brand and target_dom:
            reasons.append(f"Impersonation attempt targeting '{brand}' (legitimate domain: '{target_dom}')")

    if is_homo:
        reasons.append(f"Lookalike character substitutions detected: {', '.join(homo_chars)}")
        score = max(score, 70.0)

    final_score = min(100.0, max(0.0, score))

    return SenderAnalysisResult(
        score=round(final_score, 1),
        sender_domain=clean_domain,
        is_impersonation=is_impersonated,
        impersonated_brand=brand,
        target_domain=target_dom,
        typosquat_pattern=pattern,
        homoglyphs_detected=homo_chars,
        reasons=reasons,
    )
