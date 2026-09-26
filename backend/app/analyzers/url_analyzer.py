"""Static URL Risk Analyzer

Performs purely static, lexical, and structural risk decomposition of extracted URLs.
STRICT SAFETY INVARIANT: URLs are NEVER visited, fetched, or DNS resolved.
"""

from collections import Counter
import math
import re
from typing import List, Optional
import urllib.parse
from pydantic import BaseModel, Field
import tldextract

# High-risk / frequently abused Top-Level Domains (TLDs) in phishing campaigns
SUSPICIOUS_TLDS = {
    "xyz", "top", "buzz", "work", "click", "rest", "tk", "ml", "ga", "cf", "gq",
    "country", "stream", "download", "racing", "review", "accountant", "faith",
    "date", "party", "cricket", "trade", "science", "loan", "men", "win", "bid"
}

# Targeted brands often embedded deceptively in subdomains
TARGET_BRANDS_IN_URL = {
    "paypal", "microsoft", "apple", "google", "amazon", "netflix", "bankofamerica",
    "chase", "wellsfargo", "citi", "dhl", "fedex", "ups", "facebook", "instagram",
    "linkedin", "docusign", "coinbase", "binance", "metamask", "whatsapp", "dropbox"
}

# High-risk path tokens associated with credential harvesting pretexts
CREDENTIAL_PATH_TOKENS = {
    "login", "signin", "verify", "verification", "secure", "account", "update",
    "billing", "confirm", "wallet", "recovery", "password", "suspended", "banking",
    "auth", "authentication", "webscr", "cmd=_login-run"
}

# Regex to detect IPv4 address host
IPV4_REGEX = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")


class FlaggedURL(BaseModel):
    url: str
    risk_score: float = Field(..., ge=0.0, le=100.0)
    domain: str = ""
    subdomain: str = ""
    suffix: str = ""
    is_ip_host: bool = False
    is_punycode: bool = False
    excessive_subdomains: bool = False
    brand_in_subdomain: Optional[str] = None
    suspicious_tld: bool = False
    at_symbol_deception: bool = False
    entropy: float = 0.0
    detected_tokens: List[str] = Field(default_factory=list)
    reasons: List[str] = Field(default_factory=list)


class URLAnalysisResult(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Normalized composite URL risk score (0-100)")
    total_urls: int = 0
    high_risk_count: int = 0
    flagged_urls: List[FlaggedURL] = Field(default_factory=list)
    overall_anomalies: List[str] = Field(default_factory=list)


def calculate_shannon_entropy(text: str) -> float:
    """Calculates Shannon entropy to detect randomized or obfuscated URL segments."""
    if not text:
        return 0.0
    counts = Counter(text)
    length = len(text)
    entropy = -sum((count / length) * math.log2(count / length) for count in counts.values())
    return round(entropy, 2)


def analyze_single_url(raw_url: str) -> FlaggedURL:
    """Performs static lexical inspection on an individual URL without network requests."""
    reasons: List[str] = []
    detected_tokens: List[str] = []
    url_score = 0.0

    # Clean and parse URL
    parsed = urllib.parse.urlparse(raw_url)
    hostname = (parsed.hostname or "").lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parsed.query.lower()

    # 1. At-symbol (@) URL deception (e.g. http://google.com@attacker.com)
    at_deception = "@" in parsed.netloc
    if at_deception:
        url_score += 45.0
        reasons.append("Deceptive '@' user-info authority token present")

    # 2. Raw IP address host (e.g. http://192.168.1.1/login)
    is_ip = bool(IPV4_REGEX.match(hostname))
    if not is_ip:
        # Check for hex/octal encoded IP formats
        if re.match(r"^0x[0-9a-fA-F]+$", hostname) or hostname.replace(".", "").isdigit():
            is_ip = True
    if is_ip:
        url_score += 45.0
        reasons.append("Raw IP address used as destination host instead of registered domain")

    # 3. Punycode / IDN Homograph check
    is_puny = "xn--" in hostname
    if is_puny:
        url_score += 35.0
        reasons.append("Punycode (xn--) internationalized domain detected (potential homograph attack)")

    # 4. Extract domain details via tldextract
    ext = tldextract.extract(hostname)
    domain = ext.domain.lower()
    subdomain = ext.subdomain.lower()
    suffix = ext.suffix.lower()

    # 5. Excessive subdomains (>= 3 levels, e.g. login.verify.secure.bank.com)
    subdomain_parts = [p for p in subdomain.split(".") if p]
    excessive_subdomains = len(subdomain_parts) >= 3
    if excessive_subdomains:
        url_score += 20.0
        reasons.append(f"Excessive subdomain depth ({len(subdomain_parts)} levels)")

    # 6. Brand in subdomain deception (e.g. paypal.com.attacker.xyz)
    brand_sub = None
    for brand in TARGET_BRANDS_IN_URL:
        if brand in subdomain and brand != domain:
            brand_sub = brand
            url_score += 40.0
            reasons.append(f"Target brand '{brand}' deceptively placed in subdomain of '{domain}.{suffix}'")
            break

    # 7. Suspicious / Abused TLD check
    is_suspicious_tld = suffix in SUSPICIOUS_TLDS
    if is_suspicious_tld:
        url_score += 25.0
        reasons.append(f"Suspicious top-level domain (.{suffix}) with elevated abuse history")

    # 8. High-risk path and query keywords
    combined_path_query = path + "?" + query
    for token in CREDENTIAL_PATH_TOKENS:
        if token in combined_path_query:
            detected_tokens.append(token)
            url_score += 10.0

    if len(detected_tokens) >= 2:
        reasons.append(f"Credential harvesting keywords in URL path/query: {', '.join(detected_tokens)}")

    # 9. Shannon entropy of path
    path_entropy = calculate_shannon_entropy(path)
    if path_entropy >= 4.5 and len(path) > 20:
        url_score += 15.0
        reasons.append(f"High Shannon entropy ({path_entropy}) indicating obfuscated or randomized payload")

    final_url_score = min(100.0, max(0.0, url_score))

    return FlaggedURL(
        url=raw_url,
        risk_score=round(final_url_score, 1),
        domain=f"{domain}.{suffix}" if domain and suffix else hostname,
        subdomain=subdomain,
        suffix=suffix,
        is_ip_host=is_ip,
        is_punycode=is_puny,
        excessive_subdomains=excessive_subdomains,
        brand_in_subdomain=brand_sub,
        suspicious_tld=is_suspicious_tld,
        at_symbol_deception=at_deception,
        entropy=path_entropy,
        detected_tokens=detected_tokens,
        reasons=reasons,
    )


def analyze_urls(urls: List[str]) -> URLAnalysisResult:
    """Analyzes a list of extracted URLs statically and synthesizes a normalized aggregate risk score."""
    if not urls:
        return URLAnalysisResult(
            score=0.0,
            total_urls=0,
            high_risk_count=0,
            flagged_urls=[],
            overall_anomalies=[],
        )

    flagged: List[FlaggedURL] = []
    overall_anomalies: List[str] = []
    max_score = 0.0
    sum_score = 0.0

    for u in urls:
        item = analyze_single_url(u)
        flagged.append(item)
        if item.risk_score > max_score:
            max_score = item.risk_score
        sum_score += item.risk_score
        for r in item.reasons:
            if r not in overall_anomalies:
                overall_anomalies.append(r)

    # Aggregate: Weight towards the highest-risk URL present while factoring breadth of threat
    avg_score = sum_score / len(urls)
    composite = (0.75 * max_score) + (0.25 * avg_score)
    final_score = min(100.0, max(0.0, composite))
    high_risk_count = sum(1 for f in flagged if f.risk_score >= 50.0)

    return URLAnalysisResult(
        score=round(final_score, 1),
        total_urls=len(urls),
        high_risk_count=high_risk_count,
        flagged_urls=flagged,
        overall_anomalies=overall_anomalies,
    )
