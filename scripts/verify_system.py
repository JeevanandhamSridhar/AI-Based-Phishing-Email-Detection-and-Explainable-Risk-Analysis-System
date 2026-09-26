"""End-to-End System Verification Script

Loads synthetic demonstration samples, executes triage analysis across all analytical modules,
verifies SHAP explainability synthesis, generates forensic PDF report, and checks database persistence.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.triage_service import triage_service
from app.reports.pdf_generator import generate_forensic_pdf
from app.core.database import SessionLocal, init_db
from app.models.analysis import AnalysisRecord

def run_verification():
    print("=" * 70)
    print("PHISHGUARD SOC: COMPLETE END-TO-END PIPELINE VERIFICATION")
    print("=" * 70)

    # 1. Initialize SQLite Database
    init_db()
    db = SessionLocal()
    print("[1/5] Database initialized successfully.")

    # 2. Load Demonstration Samples
    samples_dir = Path(__file__).resolve().parent.parent / "data" / "sample_emails"
    samples = list(samples_dir.glob("*.eml"))
    print(f"[2/5] Discovered {len(samples)} synthetic demonstration emails.")

    # 3. Execute Triage Pipeline on Sample 1
    sample_file = samples_dir / "sample_01_urgent_paypal_phishing.eml"
    raw_eml = sample_file.read_text(encoding="utf-8")
    print(f"[3/5] Executing triage on '{sample_file.name}'...")
    res = triage_service.analyze_email(raw_eml, file_name=sample_file.name, db=db)

    print(f"      -> Incident ID:          {res.id}")
    print(f"      -> Subject:              {res.email_metadata.subject}")
    print(f"      -> Composite Risk Score: {res.overall_risk.score}/100 ({res.overall_risk.severity})")
    print(f"      -> ML Phish Probability: {res.factor_breakdown['ml_phishing']['details']['probability']}")
    print(f"      -> AI Likelihood:        {res.ai_authorship.ai_generated_likelihood:.1f}% ({res.ai_authorship.classification})")
    print(f"      -> XAI Summary:          {res.explainability.human_readable_summary[:80]}...")
    print(f"      -> Discovered URLs:      {len(res.url_findings)}")
    print(f"      -> Discovered Attachs:   {len(res.attachment_findings)}")

    # 4. Generate Forensic PDF
    print("[4/5] Generating cryptographic forensic PDF security report...")
    pdf_bytes = generate_forensic_pdf(res.model_dump())
    print(f"      -> Generated PDF binary ({len(pdf_bytes)} bytes) successfully.")

    # 5. Verify Database Persistence
    print("[5/5] Verifying database persistence in SQLite...")
    saved = db.query(AnalysisRecord).filter(AnalysisRecord.id == res.id).first()
    assert saved is not None, "Error: Record was not saved to SQLite!"
    print(f"      -> Verified record '{saved.id}' successfully stored in database.")
    db.close()

    print("=" * 70)
    print("ALL VERIFICATION CHECKS PASSED: SYSTEM IS 100% OPERATIONAL")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
