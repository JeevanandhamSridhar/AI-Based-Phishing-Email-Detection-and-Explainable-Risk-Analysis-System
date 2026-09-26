"""Preset Demonstration Samples Endpoint

Returns verified synthetic demonstration emails for one-click testing in the UI.
"""

from pathlib import Path
from typing import List, Dict
from fastapi import APIRouter
from app.utils.email_parser import parse_email

router = APIRouter(prefix="/samples", tags=["Demonstration Presets"])

def find_samples_dir() -> Path:
    """Finds data/sample_emails across possible runtime working directories."""
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        cand = parent / "data" / "sample_emails"
        if cand.exists() and cand.is_dir():
            return cand
    return Path("./data/sample_emails")


SAMPLES_DIR = find_samples_dir()


@router.get("", response_model=List[Dict])
async def list_sample_emails() -> List[Dict]:
    """Returns curated synthetic sample emails for immediate UI triage demonstration."""
    samples = []
    if not SAMPLES_DIR.exists():
        return samples

    for eml_file in sorted(SAMPLES_DIR.glob("*.eml")):
        try:
            content = eml_file.read_text(encoding="utf-8")
            parsed = parse_email(content, file_name=eml_file.name)
            is_phish = "phishing" in eml_file.name.lower() or "fraud" in eml_file.name.lower() or "alert" in eml_file.name.lower()

            samples.append({
                "filename": eml_file.name,
                "label": "Phishing" if is_phish else "Legitimate",
                "subject": parsed.headers.subject,
                "sender": parsed.headers.from_header,
                "raw_content": content,
                "is_synthetic": True,
            })
        except Exception:
            continue

    return samples
