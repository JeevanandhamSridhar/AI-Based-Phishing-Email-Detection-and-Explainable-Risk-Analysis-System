"""Unit Tests for Database Models and Persistence Operations
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.analysis import AnalysisRecord
from app.models.metrics import ModelMetricRecord
from app.models.adversarial import AdversarialTestRecord

# In-memory SQLite engine for fast, isolated testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_and_query_analysis_record(db_session):
    """Test saving and retrieving an email analysis triage record."""
    record = AnalysisRecord(
        subject="Urgent: Account Suspension Alert",
        sender="Security Team <security@paypa1.com>",
        sender_domain="paypa1.com",
        recipient="target@company.com",
        raw_sha256="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        risk_score=85.5,
        severity="CRITICAL",
        ml_probability=0.92,
        factor_breakdown={"ml_phishing": 27.6, "url_risk": 18.0},
        url_findings=[{"url": "http://192.168.1.1/login", "risk": 90.0}],
        header_findings={"spf": "fail", "dkim": "none"},
        attachment_findings=[],
        social_findings={"urgency": True},
        plain_explanation="High risk due to urgency and typosquatted sender domain.",
        ai_generated_likelihood=76.5,
        ai_authorship_classification="Likely LLM-Generated",
    )

    db_session.add(record)
    db_session.commit()

    retrieved = db_session.query(AnalysisRecord).filter_by(raw_sha256=record.raw_sha256).first()
    assert retrieved is not None
    assert retrieved.id == record.id
    assert retrieved.subject == "Urgent: Account Suspension Alert"
    assert retrieved.risk_score == 85.5
    assert retrieved.severity == "CRITICAL"
    assert retrieved.ai_authorship_classification == "Likely LLM-Generated"
    assert len(retrieved.url_findings) == 1
    assert retrieved.factor_breakdown["ml_phishing"] == 27.6


def test_create_and_query_model_metric_record(db_session):
    """Test saving and retrieving an ML model evaluation record."""
    record = ModelMetricRecord(
        model_name="baseline_tfidf_logistic_regression",
        evaluation_type="test_split",
        accuracy=0.965,
        precision=0.970,
        recall=0.958,
        f1_score=0.964,
        roc_auc=0.991,
        confusion_matrix={"tp": 180, "fp": 6, "tn": 194, "fn": 8},
        sample_count=388,
        metadata_info={"ngram_range": "(1,2)", "random_seed": 42},
    )

    db_session.add(record)
    db_session.commit()

    retrieved = db_session.query(ModelMetricRecord).filter_by(model_name="baseline_tfidf_logistic_regression").first()
    assert retrieved is not None
    assert retrieved.f1_score == 0.964
    assert retrieved.confusion_matrix["tp"] == 180


def test_create_and_query_adversarial_record(db_session):
    """Test saving and retrieving an adversarial evaluation experiment record."""
    record = AdversarialTestRecord(
        test_case_name="urgency_trigger_removal_01",
        original_text="Your account will be suspended within 24 hours. Click here to verify.",
        perturbed_text="Routine account review underway. Access your settings via portal.",
        removed_triggers=["suspended", "within 24 hours", "verify"],
        original_ml_prob=0.95,
        perturbed_ml_prob=0.35,
        evaded_ml=True,
        original_risk_score=88.0,
        perturbed_risk_score=55.0,
        score_drop=33.0,
        evaded_composite=False,
        details={"retained_defense": "URL and Header indicators kept score in HIGH tier"},
    )

    db_session.add(record)
    db_session.commit()

    retrieved = db_session.query(AdversarialTestRecord).filter_by(test_case_name="urgency_trigger_removal_01").first()
    assert retrieved is not None
    assert retrieved.evaded_ml is True
    assert retrieved.evaded_composite is False
    assert retrieved.score_drop == 33.0
