"""Unit Tests for Dataset Pipeline and Demonstration Fixtures
"""

import json
from pathlib import Path
import pytest
from app.utils.email_parser import parse_email

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SAMPLES_DIR = BASE_DIR / "data" / "sample_emails"
DATASET_PATH = BASE_DIR / "data" / "processed" / "emails_dataset.json"


def test_demonstration_samples_exist_and_marked_synthetic():
    """Verify that all demonstration .eml files are present and strictly marked synthetic."""
    sample_files = list(SAMPLES_DIR.glob("*.eml"))
    assert len(sample_files) >= 6

    for eml_file in sample_files:
        content = eml_file.read_text(encoding="utf-8")
        assert "X-Project-Origin: Synthetic-Educational-Sample" in content

        # Verify parsed without throwing
        parsed = parse_email(content, file_name=eml_file.name)
        assert parsed.headers.subject != ""
        assert len(parsed.sha256) == 64


def test_training_dataset_balance_and_integrity():
    """Verify that processed dataset is balanced, correctly formatted, and non-empty."""
    assert DATASET_PATH.exists()

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    assert len(records) >= 600

    phishing_count = sum(1 for r in records if r["label"] == 1)
    legit_count = sum(1 for r in records if r["label"] == 0)

    assert phishing_count == legit_count  # Perfect class balance
    assert all("text" in r and len(r["text"].strip()) > 10 for r in records)
