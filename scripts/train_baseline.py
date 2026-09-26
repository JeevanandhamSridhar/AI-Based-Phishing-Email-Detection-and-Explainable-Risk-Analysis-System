"""Baseline Phishing Classifier Training Script

Trains a TF-IDF + Logistic Regression model with fixed random seed (42),
computes genuine evaluation metrics, and serializes artifacts under models/baseline/.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split

RANDOM_SEED = 42

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "processed" / "emails_dataset.json"
OUTPUT_DIR = BASE_DIR / "models" / "baseline"


def train_baseline_model():
    """Trains the baseline TF-IDF + Logistic Regression model and serializes all artifacts."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading training data from {DATASET_PATH}...")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = [item["text"] for item in data]
    labels = [item["label"] for item in data]

    # Stratified train/test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.20, random_state=RANDOM_SEED, stratify=labels
    )
    print(f"Dataset split: {len(X_train)} training samples, {len(X_test)} evaluation samples.")

    # 1. Fit TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=10000,
        sublinear_tf=True,
        strip_accents="unicode",
        stop_words="english",
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # 2. Train Logistic Regression Classifier
    classifier = LogisticRegression(
        C=1.0,
        max_iter=1000,
        solver="lbfgs",
        random_state=RANDOM_SEED,
    )
    classifier.fit(X_train_tfidf, y_train)

    # 3. Evaluate Real Performance on Held-Out Test Set
    y_pred = classifier.predict(X_test_tfidf)
    y_pred_proba = classifier.predict_proba(X_test_tfidf)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_pred_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        "model_name": "baseline_tfidf_logistic_regression",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "random_seed": RANDOM_SEED,
        "sample_counts": {
            "total": len(texts),
            "train": len(X_train),
            "test": len(X_test),
        },
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
        },
        "confusion_matrix": {
            "matrix": cm,
            "labels": ["legitimate (0)", "phishing (1)"],
            "tn": cm[0][0],
            "fp": cm[0][1],
            "fn": cm[1][0],
            "tp": cm[1][1],
        },
    }

    metadata = {
        "model_type": "LogisticRegression",
        "vectorizer_type": "TfidfVectorizer",
        "hyperparameters": {
            "ngram_range": [1, 2],
            "max_features": 10000,
            "sublinear_tf": True,
            "C": 1.0,
            "solver": "lbfgs",
            "random_seed": RANDOM_SEED,
        },
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "vocabulary_size": len(vectorizer.vocabulary_),
    }

    # 4. Serialize Model Artifacts
    model_path = OUTPUT_DIR / "model.joblib"
    vectorizer_path = OUTPUT_DIR / "vectorizer.joblib"
    metrics_path = OUTPUT_DIR / "metrics.json"
    metadata_path = OUTPUT_DIR / "metadata.json"

    joblib.dump(classifier, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n--- Training Results (Held-Out Test Set) ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"Confusion Matrix: TN={cm[0][0]}, FP={cm[0][1]}, FN={cm[1][0]}, TP={cm[1][1]}")
    print(f"Artifacts saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    train_baseline_model()
