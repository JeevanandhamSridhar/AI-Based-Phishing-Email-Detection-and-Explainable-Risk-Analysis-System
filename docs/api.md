# REST API Specification

**Base URL:** `http://127.0.0.1:8000`  
**API Prefix:** `/api`  
**Authentication:** Local deployment (none required for local-first single-tenant SOC operation)

---

## 1. System Health

### `GET /api/health`
Returns system status, active models, version, and module readiness.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-09-26T22:30:00Z",
  "modules": {
    "parser": "ready",
    "header_analyzer": "ready",
    "url_analyzer": "ready",
    "sender_analyzer": "ready",
    "social_engineering_analyzer": "ready",
    "attachment_analyzer": "ready",
    "ml_classifier": "ready",
    "explainability_engine": "ready",
    "ai_authorship_module": "ready",
    "adversarial_module": "ready",
    "risk_engine": "ready",
    "pdf_generator": "ready"
  },
  "database": "connected"
}
```

---

## 2. Email Analysis

### `POST /api/analyze`
Analyzes an email payload (.eml raw text, plain text, or structured JSON).

**Request Body (`application/json`):**
```json
{
  "raw_email": "From: security@paypa1-update.com\nTo: user@target.com\nSubject: Urgent: Verify Account\n...",
  "file_name": "suspicious_invoice.eml"
}
```

**Alternative (`multipart/form-data`):**
- `file`: File upload (`.eml` or `.txt`)

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-09-26T22:30:00Z",
  "email_metadata": {
    "subject": "Urgent: Verify Your Account Immediately",
    "from_header": "PayPal Support <security@paypa1-update.com>",
    "sender_domain": "paypa1-update.com",
    "reply_to": "attacker-inbox@mail-drop.ru",
    "to_header": "victim@example.com",
    "date": "Sat, 26 Sep 2026 21:00:00 +0000",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "overall_risk": {
    "score": 88.5,
    "severity": "CRITICAL",
    "threshold_bracket": "75-100"
  },
  "factor_breakdown": {
    "ml_phishing": {
      "weight": 30,
      "score": 94.2,
      "weighted_contribution": 28.26,
      "probability": 0.942
    },
    "url_risk": {
      "weight": 20,
      "score": 85.0,
      "weighted_contribution": 17.00,
      "flagged_urls": [
        {
          "url": "http://192.168.1.100/verify/login.php",
          "reasons": ["Raw IP host", "Suspicious login target"],
          "risk": 90.0
        }
      ]
    },
    "header_auth": {
      "weight": 15,
      "score": 90.0,
      "weighted_contribution": 13.50,
      "spf": "fail",
      "dkim": "none",
      "dmarc": "fail",
      "reply_to_mismatch": true
    },
    "sender_domain": {
      "weight": 10,
      "score": 95.0,
      "weighted_contribution": 9.50,
      "impersonated_brand": "PayPal",
      "typosquat_pattern": "paypa1 -> paypal (Levenshtein distance: 1)",
      "lookalike_detected": true
    },
    "social_engineering": {
      "weight": 10,
      "score": 80.0,
      "weighted_contribution": 8.00,
      "triggers": ["urgency_24h", "account_suspension", "credential_verification"]
    },
    "attachment_risk": {
      "weight": 10,
      "score": 100.0,
      "weighted_contribution": 10.00,
      "attachments": [
        {
          "filename": "Invoice_Sep2026.pdf.exe",
          "extension": ".exe",
          "double_extension": true,
          "mime_type": "application/x-msdownload",
          "size_bytes": 1048576,
          "sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a"
        }
      ]
    },
    "content_anomalies": {
      "weight": 5,
      "score": 45.0,
      "weighted_contribution": 2.25,
      "anomalies": ["excessive_whitespace", "hidden_font_styling"]
    }
  },
  "explainability": {
    "method": "SHAP (LinearExplainer) + LIME cross-validation",
    "human_readable_summary": "The email exhibits critical phishing indicators characterized by high urgency language ('within 24 hours') combined with credential-harvesting triggers, an unauthenticated sender domain with typosquatting ('paypa1-update.com'), and a dangerous double-extension executable attachment.",
    "top_phishing_features": [
      {"feature": "verify account", "weight": 0.42},
      {"feature": "suspended", "weight": 0.38},
      {"feature": "immediate", "weight": 0.29},
      {"feature": "click here", "weight": 0.27}
    ],
    "top_legitimate_features": [
      {"feature": "regards", "weight": -0.05}
    ],
    "caveat": "Feature attribution is a local model explanation, not legal or definitive proof."
  },
  "ai_authorship": {
    "ai_generated_likelihood": 78.4,
    "classification": "Likely LLM-Generated",
    "stylometric_indicators": {
      "type_token_ratio": 0.74,
      "sentence_length_mean": 18.2,
      "sentence_length_variance": 4.1,
      "flesch_reading_ease": 62.4,
      "function_word_ratio": 0.48
    },
    "caveat": "Model-based indicator, not proof of AI authorship."
  }
}
```

---

## 3. Investigation History

### `GET /api/history`
Returns paginated list of prior email analyses.

**Query Parameters:**
- `page`: default 1
- `limit`: default 20
- `severity`: optional filter (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`)

### `GET /api/history/{id}`
Returns the full forensic investigation record by ID.

---

## 4. Models & Experimental Telemetry

### `GET /api/models/performance`
Returns authentic validation metrics for the baseline ML classifier (Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC).

### `GET /api/authorship/evaluate`
Returns in-generator vs. cross-generator evaluation metrics for Module A (AI authorship stylometric classifier), including transparent cross-generator degradation figures.

### `GET /api/adversarial/evaluate`
Returns evaluation results of Module B (explanation-guided adversarial rewrites), including total test cases, evasion rates, and before/after comparisons.

---

## 5. Security Reports

### `GET /api/reports/download/{id}`
Streams a cryptographically signed, ReportLab-generated forensic PDF report for the given investigation ID.
