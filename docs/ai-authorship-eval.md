# Module A: AI-Generated Phishing Authorship Evaluation

**Module Objective:** Estimate whether phishing email text was authored by a human vs. an LLM, and honestly report in-generator versus cross-generator generalization performance.

---

## 1. Methodology & Stylometric Extraction

Following the methodology outlined by **Opara et al. (2025)** (*Expert Systems with Applications* 276:127044), LLM-authored text demonstrates quantifiable structural divergence from human-authored phishing in:
1. **Low variance in sentence length:** LLM prose tends toward uniform pacing.
2. **Elevated lexical diversity (TTR) with low colloquial errors:** AI emails possess fewer grammar flaws, odd capitalization anomalies, or broken syntax.
3. **Function word bias:** High prevalence of structured transition words (`furthermore`, `additionally`, `in order to`).
4. **Normalized readability:** Flesch Reading Ease clustering tightly in the 60–75 band.

Our stylometric pipeline extracts 18 numerical features and scales them using `StandardScaler`.

---

## 2. Dataset Construction & Provenance

- **Human-Authored Phishing:** Sourced from standardized educational research subsets (colloquial errors, urgent phrasing, erratic punctuation).
- **LLM-Authored Phishing:** Synthesized locally across three distinct model architectures:
  - **Generator A:** GPT-family architecture (balanced persuasive corporate style).
  - **Generator B:** Claude-family architecture (concise, analytical notification style).
  - **Generator C (Held-out Test):** Llama/Mistral-family local architecture (informational system alerts).

*Note: All synthetic emails were generated solely for educational evaluation in an offline development environment. None were dispatched or used in external communications.*

---

## 3. Real Measured Experimental Results

*Measured via `scripts/train_authorship_classifier.py` on 2026-09-26T17:58:40.988013+00:00 (Random Seed: 42):*

### In-Generator Performance (Trained on A & B, Tested on Held-Out A & B Split)
| Metric | Value |
| :--- | :--- |
| **Accuracy** | **1.0000** |
| **Precision** | **1.0000** |
| **Recall** | **1.0000** |
| **F1-Score** | **1.0000** |
| **ROC-AUC** | **1.0000** |

### Cross-Generator Generalization (Trained on A & B, Tested on Unseen Generator C)
| Metric | Value |
| :--- | :--- |
| **Accuracy** | **0.8800** |
| **Precision** | **1.0000** |
| **Recall** | **0.7600** |
| **F1-Score** | **0.8636** |
| **Performance Drop ($\Delta F_1$)** | **+0.1364** |

---

## 4. Discussion of Generalization Degradation

As identified in the **2026 Frontiers in Big Data** study (*Cross-model evaluation of phishing detectors against LLM-generated emails*), stylometric authorship classifiers exhibit clear performance degradation when tested on unseen LLM architectures.

In our experiments:
- In-generator F1 achieved **1.0000**.
- When evaluated against the unseen generator architecture (Generator C), performance adjusted to **0.8636**, reflecting a **$\Delta F_1$ drop of +0.1364**.
- This performance drop confirms that stylometric indicators reflect specific generator syntactic habits and cannot be assumed to generalize flawlessly across arbitrary unseen LLM architectures. We report this degradation transparently as a core limitation of stylometric classification.

---

## 5. UI & API Transparency Requirements

Any output delivered to analysts via API or UI adheres strictly to these defensive standards:
1. Field name: `ai_generated_likelihood` (percentage 0–100%).
2. Accompanying caveat: **"Model-based indicator, not proof of AI authorship."**
3. Display cross-generator performance drop openly on the Model Performance dashboard.
