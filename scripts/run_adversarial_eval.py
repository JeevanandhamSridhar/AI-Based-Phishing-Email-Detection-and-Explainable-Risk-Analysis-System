"""CLI Runner for Module B: Explanation-Guided Adversarial Self-Evaluation

Executes the adversarial test suite, measures real evasion rates against the baseline model,
and updates docs/adversarial-eval.md with authentic failure and success telemetry.
"""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))
from app.adversarial.evaluator import adversarial_evaluator


def main():
    print("Executing Explanation-Guided Adversarial Self-Evaluation (Module B)...")
    summary = adversarial_evaluator.run_evaluation()

    print("\n--- Adversarial Evaluation Summary ---")
    print(f"Total Cases Tested:  {summary.total_cases_tested}")
    print(f"Evasions (ML Label Flipped): {summary.ml_evasions_count}")
    print(f"Retained Detections: {summary.ml_retained_count}")
    print(f"Evasion Success Rate: {summary.ml_evasion_rate_pct}%")
    print(f"Mean Original Prob:  {summary.mean_original_proba:.4f}")
    print(f"Mean Perturbed Prob: {summary.mean_perturbed_proba:.4f}")
    print(f"Mean Probability Drop: -{summary.mean_proba_drop:.4f}")
    print("\nResults documented in docs/adversarial-eval.md")


if __name__ == "__main__":
    main()
