"""Header & Authentication Analyzer

Evaluates email authenticity via SPF, DKIM, and DMARC status,
Return-Path/Reply-To domain alignment, and display-name spoofing heuristics.
"""

import re
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.email import HeaderInfo

# Reference list of high-value brands commonly targeted for display-name spoofing
KNOWN_TARGET_BRANDS = {
    "paypal", "microsoft", "apple", "google", "amazon", "netflix", "bank of america",
    "chase", "wells fargo", "citi", "irs", "dhl", "fedex", "ups", "facebook", "meta",
    "instagram", "linkedin", "twitter", "x", "dropbox", "docu sign", "docusign",
    "coinbase", "binance", "metamask", "whatsapp"
}


class HeaderAnalysisResult(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Normalized header risk score (0-100)")
    spf_status: str = Field(default="none", description="SPF verification result")
    dkim_status: str = Field(default="none", description="DKIM verification result")
    dmarc_status: str = Field(default="none", description="DMARC verification result")
    reply_to_mismatch: bool = False
    return_path_mismatch: bool = False
    display_name_spoofing: bool = False
    spoofed_brand_detected: Optional[str] = None
    anomalies: List[str] = Field(default_factory=list)
    details: dict = Field(default_factory=dict)


def parse_auth_mechanisms(header_info: HeaderInfo) -> tuple[str, str, str]:
    """Extracts SPF, DKIM, and DMARC states from Authentication-Results and Received-SPF."""
    auth_header = (header_info.authentication_results or "").lower()
    spf_header = (header_info.received_spf or "").lower()

    # 1. Parse SPF
    spf_status = "none"
    if "spf=pass" in auth_header or spf_header.startswith("pass"):
        spf_status = "pass"
    elif "spf=fail" in auth_header or spf_header.startswith("fail") or "spf=hardfail" in auth_header:
        spf_status = "fail"
    elif "spf=softfail" in auth_header or spf_header.startswith("softfail"):
        spf_status = "softfail"
    elif "spf=neutral" in auth_header or spf_header.startswith("neutral"):
        spf_status = "neutral"
    elif "spf=temperror" in auth_header or "spf=permerror" in auth_header:
        spf_status = "error"

    # 2. Parse DKIM
    dkim_status = "none"
    if "dkim=pass" in auth_header:
        dkim_status = "pass"
    elif "dkim=fail" in auth_header or "dkim=hardfail" in auth_header:
        dkim_status = "fail"
    elif "dkim=neutral" in auth_header or "dkim=policy" in auth_header:
        dkim_status = "neutral"
    elif "dkim=temperror" in auth_header or "dkim=permerror" in auth_header:
        dkim_status = "error"

    # 3. Parse DMARC
    dmarc_status = "none"
    if "dmarc=pass" in auth_header:
        dmarc_status = "pass"
    elif "dmarc=fail" in auth_header or "dmarc=action=reject" in auth_header or "dmarc=action=quarantine" in auth_header:
        dmarc_status = "fail"
    elif "dmarc=action=none" in auth_header:
        dmarc_status = "none"

    return spf_status, dkim_status, dmarc_status


def check_display_name_spoofing(display_name: str, sender_domain: str) -> tuple[bool, Optional[str]]:
    """Detects whether a high-profile brand is claimed in the display name while sender domain does not belong to it."""
    clean_name = display_name.lower().strip()
    clean_domain = sender_domain.lower().strip()

    for brand in KNOWN_TARGET_BRANDS:
        # Match whole brand token or normalized brand name
        brand_pattern = rf"\b{re.escape(brand)}\b"
        if re.search(brand_pattern, clean_name):
            # If the domain doesn't contain the brand, flag display name spoofing
            normalized_brand = brand.replace(" ", "")
            if normalized_brand not in clean_domain:
                return True, brand.title()

    return False, None


def analyze_headers(header_info: HeaderInfo) -> HeaderAnalysisResult:
    """Analyzes email authentication records and structural header alignments."""
    spf_status, dkim_status, dmarc_status = parse_auth_mechanisms(header_info)
    anomalies: List[str] = []
    base_score = 0.0

    sender_dom = (header_info.sender_domain or "").lower()
    reply_to_dom = (header_info.reply_to_domain or "").lower()
    return_path_dom = (header_info.return_path_domain or "").lower()

    # 1. Evaluate SPF status
    if spf_status == "fail":
        base_score += 35.0
        anomalies.append("SPF verification failed (sender IP not authorized for domain)")
    elif spf_status == "softfail":
        base_score += 20.0
        anomalies.append("SPF softfail recorded")
    elif spf_status == "none" and sender_dom:
        base_score += 10.0
        anomalies.append("No SPF verification records detected")

    # 2. Evaluate DKIM status
    if dkim_status == "fail":
        base_score += 30.0
        anomalies.append("DKIM cryptographic signature verification failed")
    elif dkim_status == "none" and sender_dom:
        base_score += 10.0
        anomalies.append("No DKIM signature detected")

    # 3. Evaluate DMARC status
    if dmarc_status == "fail":
        base_score += 35.0
        anomalies.append("DMARC alignment failure")

    # 4. Evaluate Domain Alignments
    reply_to_mismatch = False
    if reply_to_dom and sender_dom and reply_to_dom != sender_dom:
        # Don't flag if it's merely a subdomain relationship
        if not (reply_to_dom.endswith("." + sender_dom) or sender_dom.endswith("." + reply_to_dom)):
            reply_to_mismatch = True
            base_score += 25.0
            anomalies.append(f"Reply-To domain mismatch: claims '{sender_dom}' but replies route to '{reply_to_dom}'")

    return_path_mismatch = False
    if return_path_dom and sender_dom and return_path_dom != sender_dom:
        if not (return_path_dom.endswith("." + sender_dom) or sender_dom.endswith("." + return_path_dom)):
            return_path_mismatch = True
            base_score += 15.0
            anomalies.append(f"Return-Path envelope domain mismatch: '{sender_dom}' vs '{return_path_dom}'")

    # 5. Evaluate Display Name Spoofing
    display_spoofed, spoofed_brand = check_display_name_spoofing(
        header_info.sender_name,
        header_info.sender_domain,
    )
    if display_spoofed:
        base_score += 40.0
        anomalies.append(f"Display name impersonation: claims identity of '{spoofed_brand}' from unrelated domain '{sender_dom}'")

    # 6. Check for missing essential headers
    if not header_info.from_header:
        base_score += 20.0
        anomalies.append("Missing mandatory RFC-822 'From' header")
    if not header_info.subject or header_info.subject == "(No Subject)":
        base_score += 5.0

    # If all authentications passed and no anomalies, reward clean record
    if spf_status == "pass" and dkim_status == "pass" and not reply_to_mismatch and not display_spoofed:
        base_score = max(0.0, base_score - 20.0)

    final_score = min(100.0, max(0.0, base_score))

    return HeaderAnalysisResult(
        score=round(final_score, 1),
        spf_status=spf_status,
        dkim_status=dkim_status,
        dmarc_status=dmarc_status,
        reply_to_mismatch=reply_to_mismatch,
        return_path_mismatch=return_path_mismatch,
        display_name_spoofing=display_spoofed,
        spoofed_brand_detected=spoofed_brand,
        anomalies=anomalies,
        details={
            "sender_domain": sender_dom,
            "reply_to_domain": reply_to_dom,
            "return_path_domain": return_path_dom,
        },
    )
