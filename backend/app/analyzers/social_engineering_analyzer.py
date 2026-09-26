"""Social-Engineering Rule-Based Analyzer

Detects psychological coercion, artificial urgency, fear appeals, authority impersonation,
and credential harvesting language patterns using structured regex taxonomies.
"""

import re
from typing import Dict, List
from pydantic import BaseModel, Field

# Categorized taxonomy of social engineering trigger regex patterns
SOCIAL_ENGINEERING_TAXONOMY: Dict[str, Dict[str, any]] = {
    "urgency": {
        "weight": 25.0,
        "label": "Artificial Urgency & Time Scarcity",
        "patterns": [
            r"\b(?:within\s+(?:24|48|12|2|1)\s*hours?)\b",
            r"\b(?:immediate(?:ly)?\s+(?:action|attention|response|update))\b",
            r"\b(?:act\s+now|urgent(?:ly)?|expires?\s+(?:today|soon|within))\b",
            r"\b(?:final\s+(?:notice|warning|reminder))\b",
            r"\b(?:don'?t\s+delay|limited\s+time|time\s+is\s+running\s+out)\b",
        ],
    },
    "threat_fear": {
        "weight": 25.0,
        "label": "Fear, Coercion & Account Termination",
        "patterns": [
            r"\b(?:account\s+(?:suspended|restricted|locked|frozen|disabled|terminated))\b",
            r"\b(?:unauthorized\s+(?:access|activity|charges?|login|transactions?))\b",
            r"\b(?:security\s+(?:alert|breach|incident|compromised?))\b",
            r"\b(?:permanent\s+(?:deletion|closure|termination))\b",
            r"\b(?:legal\s+(?:action|proceedings|consequences)|law\s+enforcement|warrant)\b",
        ],
    },
    "credential_harvesting": {
        "weight": 30.0,
        "label": "Credential & Sensitive Data Solicitation",
        "patterns": [
            r"\b(?:verify\s+(?:your\s+)?(?:account|identity|email|details|credentials?))\b",
            r"\b(?:confirm\s+(?:your\s+)?(?:password|pin|ssn|billing|information))\b",
            r"\b(?:click\s+(?:here|the\s+link\s+below)\s+to\s+(?:login|verify|confirm|restore))\b",
            r"\b(?:update\s+(?:your\s+)?(?:payment|banking|credit\s+card|profile))\b",
            r"\b(?:re-?authenticate|validate\s+(?:access|credentials?))\b",
        ],
    },
    "financial_bait": {
        "weight": 20.0,
        "label": "Unsolicited Financial Bait & Extortion",
        "patterns": [
            r"\b(?:unclaimed\s+(?:funds?|prize|inheritance|lottery|reward))\b",
            r"\b(?:million\s+(?:dollars?|usd|euros?|pounds?))\b",
            r"\b(?:wire\s+transfer\s+refund|compensation\s+payout)\b",
            r"\b(?:bitcoin\s+(?:wallet|payment|address)|send\s+btc)\b",
            r"\b(?:recorded\s+you|compromised\s+webcam|extortion)\b",
        ],
    },
    "authority_impersonation": {
        "weight": 15.0,
        "label": "Authority & IT Administrator Pretext",
        "patterns": [
            r"\b(?:it\s+(?:administrator|helpdesk|support\s+desk|dept|department))\b",
            r"\b(?:system\s+(?:administrator|upgrade\s+notice|maintenance\s+protocol))\b",
            r"\b(?:mandatory\s+(?:security\s+update|compliance\s+check))\b",
            r"\b(?:executive\s+office|ceo\s+(?:request|mandate))\b",
        ],
    },
}


class TriggerCategoryMatch(BaseModel):
    category: str
    label: str
    matches_found: List[str] = Field(default_factory=list)
    category_score: float = 0.0


class SocialEngineeringResult(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Normalized social-engineering risk score (0-100)")
    categories_flagged: List[str] = Field(default_factory=list)
    detailed_matches: List[TriggerCategoryMatch] = Field(default_factory=list)
    total_triggers_count: int = 0
    reasons: List[str] = Field(default_factory=list)


def analyze_social_engineering(subject: str, body: str) -> SocialEngineeringResult:
    """Scans email subject and body for coercive social engineering linguistic triggers."""
    combined_text = f"{subject}\n{body}".lower()
    total_triggers = 0
    calculated_score = 0.0
    detailed_matches: List[TriggerCategoryMatch] = []
    categories_flagged: List[str] = []
    reasons: List[str] = []

    for cat_key, cat_data in SOCIAL_ENGINEERING_TAXONOMY.items():
        found_in_category = []
        for pat in cat_data["patterns"]:
            matches = re.findall(pat, combined_text, flags=re.IGNORECASE)
            if matches:
                # Deduplicate matching snippets
                for m in matches:
                    if isinstance(m, tuple):
                        m = " ".join([part for part in m if part])
                    m_clean = m.strip()
                    if m_clean and m_clean not in found_in_category:
                        found_in_category.append(m_clean)

        if found_in_category:
            total_triggers += len(found_in_category)
            cat_weight = cat_data["weight"]
            # Sub-score proportional to number of triggers, capped at weight * 1.5
            cat_score = min(cat_weight * 1.5, cat_weight + (len(found_in_category) - 1) * 5.0)
            calculated_score += cat_score

            categories_flagged.append(cat_key)
            reasons.append(f"{cat_data['label']} detected: '{', '.join(found_in_category)}'")
            detailed_matches.append(
                TriggerCategoryMatch(
                    category=cat_key,
                    label=cat_data["label"],
                    matches_found=found_in_category,
                    category_score=round(cat_score, 1),
                )
            )

    # Multi-category reinforcement bonus: if an email combines urgency AND credential harvesting AND threats,
    # that is the signature triad of phishing
    if "urgency" in categories_flagged and "credential_harvesting" in categories_flagged:
        calculated_score += 15.0
        reasons.append("Coercive Triad: Combines urgency pressure with credential solicitation")

    if "threat_fear" in categories_flagged and "credential_harvesting" in categories_flagged:
        calculated_score += 15.0

    final_score = min(100.0, max(0.0, calculated_score))

    return SocialEngineeringResult(
        score=round(final_score, 1),
        categories_flagged=categories_flagged,
        detailed_matches=detailed_matches,
        total_triggers_count=total_triggers,
        reasons=reasons,
    )
