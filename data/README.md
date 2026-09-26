# Data Governance & Provenance Guide

## 1. Directory Structure

```
data/
├── raw/                      # Public research datasets (e.g. Nazario, Enron subsets)
├── processed/                # Normalized, sanitized text & metadata for training
├── sample_emails/            # Curated synthetic demonstration emails (.eml / .txt)
└── llm_generated_samples/    # Locally created synthetic LLM samples for Module A evaluation
```

---

## 2. Ethical Guidelines & Safety Protocols

> **CRITICAL INSTRUCTION:**  
> All sample emails and LLM-generated phishing instances contained within this repository are created strictly for local academic research, educational demonstrations, and model evaluation within an isolated offline environment.  
> **Under no circumstances should any generated email or sample be dispatched, sent across any network, or used for real-world social engineering.**

---

## 3. Dataset Classes & Provenance

### Human-Written Legitimate & Phishing Corpora:
- Standardized from recognized academic repositories (e.g., Nazario Phishing Corpus and public domain email collections).
- Transmission noise, internal IP addresses, and private recipient information are sanitized and replaced with placeholder targets (`victim@example.com`).

### LLM-Generated Phishing Samples (Module A Evaluation):
- Synthesized locally across 3 distinct model architectures:
  - `Generator_A/` (GPT-family style): Formal, authoritative corporate notifications.
  - `Generator_B/` (Claude-family style): Technical alerts, system upgrades, account synching.
  - `Generator_C/` (Llama/Mistral local open-source style): Minimalist password expirations and billing notices.
- Used strictly for evaluating in-generator vs. cross-generator generalization degradation.

---

## 4. Synthetic Labeling Invariant
All test fixtures and demonstration emails stored under `data/sample_emails/` contain an explicit RFC-822 header marker:
`X-Project-Origin: Synthetic-Educational-Sample`
This ensures test data cannot be mistaken for real captured threat intelligence.
