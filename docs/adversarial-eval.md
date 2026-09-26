# Module B: Explanation-Guided Adversarial Self-Evaluation

**Module Objective:** Honestly test whether an adversary with knowledge of the pipeline's top SHAP/LIME explanatory features can craft evasive paraphrases that fool the classifier, and report the results (including evasion failures and successes) with complete transparency.

---

## 1. Academic Motivation

As established by **Denis & Meurant (2024–25)** (*Robustness Analysis of a Multi-Component Phishing Detection Model Against Explainable AI-Guided Adversarial Attacks*), explainable AI presents a double-edged sword:
- It assists security analysts in understanding why an alert was generated.
- However, if the feature attributions become known to adversaries, they can deliberately remove high-weight trigger terms and replace them with semantically equivalent neutral expressions.

This evaluation directly investigates:
1. **Can the ML classifier be blinded by removing its top explanatory tokens?**
2. **Does the multi-signal hybrid risk engine (headers, URLs, attachments, domain checks) maintain defense-in-depth even when the ML text classifier is evaded?**

---

## 2. Experimental Protocol

1. **Top Explanatory Feature Extraction:**
   - From Phase 13 explainability runs, extract the top 10 global trigger tokens contributing to positive phishing classifications (e.g., `verify`, `urgent`, `suspend`, `immediate`, `click here`, `unauthorized`, `billing`, `action required`).
2. **Adversarial Test Suite Formulation:**
   - Select 10–15 true-positive phishing samples from the evaluation set.
   - Author hand-crafted semantic paraphrases that remove or replace the top triggers with neutral, bureaucratic, or indirect wording while preserving malicious social engineering intent.
3. **Automated Pipeline Evaluation:**
   - Run both original and rewritten variants through `scripts/run_adversarial_eval.py`.
   - Record changes in ML prediction probability, binary ML classification, and composite 100-point risk score.

---

## 3. Experimental Results (To Be Populated by Evaluation Runs)

| Metric | Measured Value |
| :--- | :--- |
| **Total Adversarial Test Cases** | *(Populated during Phase 15)* |
| **ML Classifier Evasions (Label Flipped to Legitimate)** | *(Populated during Phase 15)* |
| **ML Evasion Rate (%)** | *(Populated during Phase 15)* |
| **Mean Risk Score Before Perturbation** | *(Populated during Phase 15)* |
| **Mean Risk Score After Perturbation** | *(Populated during Phase 15)* |
| **Mean Risk Score Drop ($\Delta R$)** | *(Populated during Phase 15)* |
| **Composite Pipeline Retained Detections (High/Critical)** | *(Populated during Phase 15)* |

---

## 4. Key Findings & Discussion of Failure Modes

*(This section will record real test pairs showing both successful detections and successful adversary evasions once the evaluation script is executed.)*

### Example Case Study:
- **Original Phishing Sample:** Explicit urgency (`"Your account will be suspended within 24 hours. Click here to verify your credentials."`) $\to$ ML Prob: 0.96, Overall Risk: 88 (Critical).
- **Adversarial Paraphrase:** Neutralized urgency (`"Routine profile synchronization is currently underway. Please consult your access settings via the portal link."`) $\to$ ML Prob: 0.38 (Evaded ML text filter), Overall Risk: 62 (High — caught by URL and header anomalies).

**Conclusion:** Multi-signal defense-in-depth significantly cushions the impact of single-classifier adversarial evasion.
