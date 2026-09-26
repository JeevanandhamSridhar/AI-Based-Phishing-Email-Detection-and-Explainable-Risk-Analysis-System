"""Independent ML Model Evaluation Script

Loads the trained baseline model, evaluates performance across test samples,
computes authentic metrics, and persists the record into the database.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "processed" / "emails_dataset.json"
MODEL_DIR = BASE_DIR / "models" / "baseline"


def run_evaluation():
    """Runs rigorous model evaluation on the baseline classifier."""
    model_path = MODEL_DIR / "model.joblib"
    vectorizer_path = MODEL_DIR / "vectorizer.joblib"
    metrics_path = MODEL_DIR / "metrics.json"

    if not model_path.exists() or not vectorizer_path.exists():
        print(f"Error: Model artifacts not found in {MODEL_DIR}. Please run scripts/train_baseline.py first.")
        return

    classifier = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = [item["text"] for item in data]
    labels = [item["label"] for item in data]

    # Use fixed test split (seed 42)
    _, X_test, _, y_test = train_test_split(
        texts, labels, test_size=0.20, random_state=42, stratify=labels
    )

    X_test_tfidf = vectorizer.transform(X_test)
    y_pred = classifier.predict(X_test_tfidf)
    y_pred_proba = classifier.predict_proba(X_test_tfidf)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_pred_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()

    eval_results = {
        "model_name": "baseline_tfidf_logistic_regression",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evaluation_type": "held_out_test_split",
        "sample_count": len(y_test),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "confusion_matrix": {
            "tn": cm[0][0],
            "fp": cm[0][1],
            "fn": cm[1][0],
            "tp": cm[1][1],
        },
    }

    # Save to metrics.json
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    print("--- Model Evaluation Summary ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"Confusion Matrix: TN={cm[0][0]}, FP={cm[0][1]}, FN={cm[1][0]}, TP={cm[1][1]}")


if __name__ == "__main__":
    run_evaluation()
