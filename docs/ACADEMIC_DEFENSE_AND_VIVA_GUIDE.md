# PhishGuard SOC: Academic Defense, Literature Positioning & Viva Examination Guide

This document preserves the comprehensive academic positioning, literature review, theoretical justifications, defensive safety guarantees, and examiner viva examination cheat sheet for the **AI-Based Phishing Email Detection and Explainable Risk Analysis System**.

---

## 1. Verbatim Academic Literature Positioning

> **Defensible Research Framing (Verbatim):**  
> *"In the literature reviewed for this project, we did not find a single locally-deployable, budget-constrained student system that combines multi-signal explainable phishing risk scoring with an explicit AI-authorship indicator and a self-directed adversarial evasion test. The individual techniques are established; the integration and the honest reporting of their limits is the contribution."*

No claim of "first ever" is made. The underlying components—rule-based header analysis, heuristic lexical inspection, supervised machine learning, SHAP/LIME feature attributions, and stylometric modeling—are documented in enterprise platforms and academic literature. This project synthesizes these analytical vectors into an offline, local-first platform running on standard commodity hardware (Rs. 0 software budget) while empirically disclosing its generalization degradation and adversarial fragility.

---

## 2. Strict Defensive Safety Invariants

| Safety Invariant | Technical Enforcement Mechanism | Threat Vector Mitigated |
| :--- | :--- | :--- |
| **Zero URL Visiting** | Static regex extraction, domain parsing, and Shannon entropy computation only. No DNS lookup, no HTTP GET/POST, no TCP socket connection. | Web tracking beacons, drive-by downloads, attacker IP disclosure, canary token activation. |
| **Zero Attachment Execution** | Passive binary inspection for double extensions (`.pdf.exe`), macro type identifiers (`.docm`), and cryptographic SHA-256 fingerprinting. No sandbox execution, no binary detonation. | Ransomware execution, reverse shell spawns, macro execution, memory injection. |
| **Zero External Data Exfiltration** | SQLite local persistence, in-process Scikit-learn inference, local CPU SHAP attribution, and local ReportLab PDF compilation. Zero outbound API calls. | PII leakage, corporate credential leakage, telemetry spying, cloud API vendor lock-in. |

---

## 3. Comprehensive Comparative Analysis: 10 Recent Published Research Papers (2024–2026)

| # | Paper Citation & Venue | Key Architectural Features Introduced | What Changes / Innovations It Made | Identified Limitations & Gaps | How Our System Differentiates / Highlights |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Lim et al. (2025)**<br>*EXPLICATE*<br>arXiv:2503.20796 | Pairs ML classifiers with SHAP & LIME; passes attribution tokens to an LLM to generate plain-English user explanations; ships as a browser extension & GUI (~98% accuracy). | Pioneered accessible natural language explanations for non-technical users derived from raw mathematical attributions. | Requires cloud LLM API connectivity; introduces recurring per-query financial cost; lacks AI authorship detection and adversarial self-testing. | **Local-First & Offline:** Generates rule-synthesized plain English rationale in-process at Rs. 0 cost; adds Module A (AI authorship) and Module B (adversarial testing). |
| **2** | **MultiPhishGuard (2025)**<br>arXiv:2505.23803 | Multi-agent collaborative LLM architecture where specialized agent personas (header agent, body agent, link agent) debate and reach consensus. | Replaced monolithic classifiers with multi-angle conversational reasoning. | High inference latency (3–8 seconds per email); non-deterministic decisions; requires high-end GPU or commercial cloud endpoints. | **Deterministic Sub-Second Latency:** Uses 7-factor weighted hybrid scoring combining fast static heuristics with calibrated ML, executing in <200ms on CPU. |
| **3** | **ETASR Hybrid Framework (2025)**<br>Vol. 15, No. 5 | Combines SPF/DKIM/DMARC email authentication records, static URL lexical properties, and machine learning models (>95% accuracy). | Formally demonstrated that combining authentication headers with URL and NLP features significantly reduces false positive rates. | Static heuristic rules only; treats ML as a black box without explainability; assumes human-authored phishing text. | **Explainability + Authorship:** Integrates SHAP token attribution directly with an 18-feature stylometric AI authorship estimator. |
| **4** | **Fatima et al. (2025)**<br>ETASR 15(5) | Evaluates SHAP and LIME across multiple ML algorithms (Random Forest, SVM, XGBoost) for constrained networked IoT devices. | Benchmarked computational overhead of XAI methods in hardware-restricted settings. | Evaluated only isolated feature attributions; did not construct an end-to-end user triage system; did not test adversarial evasion. | **Full SOC Workflow:** Implements end-to-end triage from raw RFC-822 MIME parsing to cryptographic PDF incident export. |
| **5** | **Opara et al. (2025)**<br>*Expert Systems with Applications*, 276 | Stylometric feature extraction (Type-Token Ratio, Hapax Legomena, sentence variance, readability indices) to separate human vs. AI phishing emails (~96% accuracy). | Demonstrated that LLMs exhibit distinct stylometric footprints (low lexical variance, higher formality) detectable via classic NLP. | Evaluated only in-distribution (homogeneous model in training and testing); did not evaluate cross-model transferability. | **Honest Generalization Testing:** Module A explicitly tests zero-shot transfer against unseen LLM architectures, documenting the 13.6% F1 performance drop. |
| **6** | **Frontiers in Big Data (2026)**<br>*Cross-Model Evaluation* | Evaluates classifiers trained on one LLM's phishing samples when tested against emails generated by distinct, unseen LLM families. | Proved that stylometric detectors experience catastrophic performance drops when facing unfamiliar LLM generation styles. | Pure empirical paper; offered no defensive mitigation framework or hybrid integration with header/URL signals. | **Multi-Signal Defense-in-Depth:** Integrates AI authorship as an advisory signal alongside 6 other independent vectors so that evasion of one factor does not bypass triage. |
| **7** | **Koide et al. (2024/2026)**<br>*ChatSpamDetector*<br>Springer LNCS | Leverages few-shot prompting of large language models for contextual phishing and spam identification. | Captured nuanced semantic subtexts and social engineering persuasion strategies without feature engineering. | Impractical for high-throughput enterprise gateways; vulnerable to prompt injection; transmits sensitive email contents externally. | **Strict Local Isolation:** Operates 100% offline; eliminates data exfiltration and prompt injection attack vectors. |
| **8** | **Denis & Meurant (2024–25)**<br>MSc Thesis, EPL | Analyzes the security risks of XAI by demonstrating that adversaries who observe top SHAP features can evade detection via semantic paraphrasing. | First comprehensive demonstration that feature explanations provide an adversarial roadmap for evading phishing classifiers. | Offline academic thesis; did not provide a defensive operational dashboard or automated self-evaluation harness. | **Module B Adversarial Self-Evaluation:** Built directly into the platform to measure and report its own evasion vulnerability transparently. |
| **9** | **PiMRef (2025)**<br>arXiv:2507.15393 | Spear-phishing detection using organizational knowledge-base invariants to detect impersonation of trusted internal identities. | Shifted focus from generic spam tokens to organizational context and relationship graphs. | Requires extensive enterprise directory access, employee historical archives, and custom tenant baselining. | **Zero-Configuration Triage:** Operates instantaneously on arbitrary `.eml` files without pre-existing organizational baselines or tenant access. |
| **10** | **MeAJOR Corpus (2025)**<br>arXiv:2507.17978 | Standardized multi-source phishing email benchmark preserving full RFC-822 headers, MIME parts, and raw URLs. | Addressed the widespread flaw in research datasets that discard email headers and retain only raw body text. | Benchmark dataset paper; did not construct an analytical triage platform or explainable risk engine. | **Full RFC-822 Compliance:** Our static parser extracts multi-part headers, attachments, and URLs directly from standard RFC-822 envelopes. |

---

## 4. Examiner Viva Q&A Cheat Sheet

### Q1: Why didn’t you use a Transformer model like BERT, RoBERTa, or a local 7B LLM?
**Answer:**  
In a practical security operations center (SOC) triage environment, three constraints dominate:
1. **Deterministic Latency:** TF-IDF + Logistic Regression evaluates an email in under 5 milliseconds on CPU, compared to 500ms–5s for transformers.
2. **Exact Mathematical Attribution:** SHAP's `LinearExplainer` computes mathematically exact Shapley values directly from the model's coefficients in closed form ($O(F)$ time). On deep models, SHAP must use `KernelExplainer` or `SamplingExplainer`, which are approximations, take up to 2 minutes per email, and fluctuate between runs.
3. **Hardware Independence:** The system runs smoothly on standard low-power laptops with zero GPU requirements, adhering to the Rs. 0 budget constraint.

### Q2: What is the exact scientific value of Module A (AI Authorship Indicator)?
**Answer:**  
Most published papers report overly optimistic detection rates (~96–98%) by training and testing on emails generated by the same LLM family. Module A extracts 18 stylometric features and implements a cross-generator validation protocol. We train on Generators A & B and evaluate on held-out Generator C. We empirically demonstrate that accuracy drops from 100% to 88.0% and F1 drops from 1.0 to 0.8636 ($\Delta F_1 = 0.1364$). This proves that stylometric features capture model-specific tokenization artifacts rather than universal AI signatures—a critical, honest insight for real-world deployment.

### Q3: What is the scientific value of Module B (Adversarial Self-Evaluation)?
**Answer:**  
Explainability is usually presented as a pure defense. However, if a defender can see why a model flagged an email, so can an attacker. Module B takes the top positive SHAP trigger tokens (e.g., "urgent", "suspended", "verify") and applies explanation-guided semantic paraphrasing. Our test battery demonstrates a 10% complete evasion rate and an average 20.3% drop in detection confidence. Rather than hiding this limitation, our platform openly reports it and proves why multi-factor defense-in-depth (combining headers, URLs, and typosquatting with ML) is essential.

### Q4: How is the composite 0–100 risk score calculated?
**Answer:**  
The score integrates 7 independent analytical vectors with configurable weights totaling 100.0:
- ML Phishing Probability: **30 pts**
- Static URL Heuristic Risk: **20 pts**
- Header & Authentication (SPF/DKIM/DMARC): **15 pts**
- Sender Domain Typosquatting / Homoglyphs: **10 pts**
- Social Engineering Linguistic Markers: **10 pts**
- Static Attachment Screening: **10 pts**
- Content Obfuscation (Hidden CSS, Zero-width Unicode): **5 pts**

Severity brackets are strictly mapped: Low (0–24), Moderate (25–49), High (50–74), Critical (75–100).
