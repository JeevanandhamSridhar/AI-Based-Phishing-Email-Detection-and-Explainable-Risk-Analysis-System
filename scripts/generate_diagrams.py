import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "reports", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def style_fig(title_text):
    fig, ax = plt.subplots(figsize=(14, 8.5), dpi=300)
    ax.set_facecolor("#f8fafc")
    fig.patch.set_facecolor("#ffffff")
    ax.axis('off')
    plt.title(title_text, fontsize=14, fontweight='bold', pad=18, color="#0f172a", fontfamily='sans-serif')
    return fig, ax

# =====================================================================
# FIGURE 1: END-TO-END SYSTEM ARCHITECTURE
# =====================================================================
def generate_fig1_end_to_end():
    fig, ax = style_fig("Figure 1: End-to-End System Architecture of PhishGuard SOC")

    # Layer boxes
    layers = [
        ("Layer 1: Presentation & Cyber-SOC Dashboard", 0.81, 0.14, "#e0e7ff", "#4338ca",
         ["React 18 SPA (Vite 5)", "Cyber-SOC Terminal HUD", "In-Body XAI Highlighter", "Animated SVG Risk Meter", "Investigation Ledger"]),
        ("Layer 2: API Gateway & Validation Layer", 0.63, 0.14, "#ecfdf5", "#059669",
         ["FastAPI REST Endpoints", "Uvicorn ASGI Engine", "Pydantic v2 Data Schemas", "CORS & Auth Middleware", "Zero-Fetch Request Enforcer"]),
        ("Layer 3: Static Decomposer & Multi-Signal Analyzers", 0.45, 0.14, "#fef3c7", "#d97706",
         ["RFC-822 MIME Parser", "Passive URL Entropy Heuristics", "SPF/DKIM/DMARC Auth Engine", "Social Engineering NLP", "SHA-256 Attachment Fingerprinter"]),
        ("Layer 4: AI & Explainability Compute Core", 0.27, 0.14, "#f3e8ff", "#7e22ce",
         ["TF-IDF + Logistic Regression", "SHAP LinearExplainer Engine", "Module A: Stylometric Authorship", "Module B: Adversarial Stress-Tester", "Rule-Template Synthesizer"]),
        ("Layer 5: Risk Fusion & Persistent Storage", 0.09, 0.14, "#fee2e2", "#dc2626",
         ["5-Vector Weighted Risk Engine", "Non-Linear Override Penalties", "SQLite Relational Store (SQLAlchemy)", "ReportLab PDF Engine", "JSON Telemetry Cache"])
    ]

    for title, y, h, bg, border, items in layers:
        rect = patches.FancyBboxPatch((0.05, y), 0.90, h, boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor=bg, edgecolor=border, linewidth=2, zorder=2)
        ax.add_patch(rect)
        # Title
        ax.text(0.07, y + h - 0.035, title, fontsize=9.5, fontweight='bold', color=border, zorder=3, va='top')
        
        # Items boxes
        item_w = 0.165
        for idx, it in enumerate(items):
            ix = 0.07 + idx * 0.176
            iy = y + 0.02
            ibox = patches.Rectangle((ix, iy), item_w, 0.055, facecolor="#ffffff", edgecolor="#cbd5e1", lw=1.2, zorder=3)
            ax.add_patch(ibox)
            ax.text(ix + item_w/2, iy + 0.027, it, fontsize=7.2, color="#1e293b", fontweight='bold',
                    ha='center', va='center', zorder=4)

    # Connecting vertical arrows
    for y_conn in [0.81, 0.63, 0.45, 0.27]:
        ax.annotate("", xy=(0.50, y_conn), xytext=(0.50, y_conn + 0.01),
                    arrowprops=dict(arrowstyle="<->", color="#334155", lw=2))

    path = os.path.join(OUTPUT_DIR, "fig1_end_to_end_architecture.png")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Generated {path}")

# =====================================================================
# FIGURE 2: WORKFLOW ARCHITECTURE
# =====================================================================
def generate_fig2_workflow():
    fig, ax = style_fig("Figure 2: Complete Threat Triage Workflow Architecture")

    steps = [
        ("Step 1: Input Ingestion", "Raw RFC-822 / .EML Drop\nOr Text Paste / Presets", 0.04, 0.72, "#dbeafe", "#2563eb"),
        ("Step 2: Defensive Gate", "Zero-Outbound Socket Block\nAnti-Detonation Isolation", 0.28, 0.72, "#dcfce7", "#16a34a"),
        ("Step 3: Static MIME Parse", "Unwrap Boundaries (--boundary)\nSeparate Body, URLs, Attachs", 0.52, 0.72, "#fef3c7", "#d97706"),
        ("Step 4: Vector Analysis", "5 Analyzers in Parallel:\nML, URLs, Auth, Social, Files", 0.76, 0.72, "#f3e8ff", "#9333ea"),
        
        ("Step 5: XAI & Stylometry", "SHAP Game-Theoretic Values\nModule A AI Likelihood %", 0.76, 0.22, "#ffedd5", "#ea580c"),
        ("Step 6: Risk Fusion", "Composite Weighted Score\nNon-Linear Overrides (+20)", 0.52, 0.22, "#e0e7ff", "#4338ca"),
        ("Step 7: Threshold Verdict", "Legitimate (<25) / Suspicious\nOr Phishing Threat (>=50)", 0.28, 0.22, "#fee2e2", "#dc2626"),
        ("Step 8: Output & Report", "In-Body Highlighting, SQLite\n& Tamper-Proof PDF Export", 0.04, 0.22, "#ccfbf1", "#0d9488")
    ]

    for title, desc, x, y, bg, border in steps:
        rect = patches.FancyBboxPatch((x, y), 0.20, 0.20, boxstyle="round,pad=0.02,rounding_size=0.03",
                                      facecolor=bg, edgecolor=border, linewidth=2, zorder=2)
        ax.add_patch(rect)
        ax.text(x + 0.10, y + 0.16, title, fontsize=8.5, fontweight='bold', color=border, ha='center', va='center', zorder=3)
        ax.text(x + 0.10, y + 0.08, desc, fontsize=7.5, color="#1e293b", ha='center', va='center', zorder=3)

    # Horizontal Flow Arrows (Top: 1 -> 2 -> 3 -> 4)
    def arrow(x1, y1, x2, y2, color="#475569"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=2))

    arrow(0.24, 0.82, 0.28, 0.82)
    arrow(0.48, 0.82, 0.52, 0.82)
    arrow(0.72, 0.82, 0.76, 0.82)

    # Downward connection (4 -> 5)
    arrow(0.86, 0.72, 0.86, 0.42)

    # Horizontal Flow Arrows (Bottom: 5 -> 6 -> 7 -> 8)
    arrow(0.76, 0.32, 0.72, 0.32)
    arrow(0.52, 0.32, 0.48, 0.32)
    arrow(0.28, 0.32, 0.24, 0.32)

    path = os.path.join(OUTPUT_DIR, "fig2_workflow_architecture.png")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Generated {path}")

# =====================================================================
# FIGURE 3: DATA FLOW DIAGRAM (DFD LEVEL 0 & LEVEL 1)
# =====================================================================
def generate_fig3_dfd():
    fig, ax = style_fig("Figure 3: Data Flow Diagram (DFD Level 0 Context & Level 1 Subsystems)")

    def draw_entity(x, y, w, h, text, bg="#e0e7ff", border="#4338ca"):
        rect = patches.Rectangle((x, y), w, h, facecolor=bg, edgecolor=border, linewidth=2, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, fontsize=9, fontweight='bold', color="#1e1b4b", ha='center', va='center', zorder=3)

    def draw_proc(x, y, r, p_num, text, bg="#dcfce7", border="#059669"):
        circle = patches.Circle((x, y), r, facecolor=bg, edgecolor=border, linewidth=2, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, f"P{p_num}\n{text}", fontsize=8, fontweight='bold', color="#064e3b", ha='center', va='center', zorder=3)

    def draw_store(x, y, w, h, store_name, bg="#fef3c7", border="#d97706"):
        rect = patches.Rectangle((x, y), w, h, facecolor=bg, edgecolor=border, linewidth=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, store_name, fontsize=8, fontweight='bold', color="#78350f", ha='center', va='center', zorder=3)

    # Entities
    draw_entity(0.04, 0.68, 0.16, 0.14, "Security Analyst\n(React Web UI)")
    draw_entity(0.04, 0.24, 0.16, 0.14, "Mail Client Source\n(.EML / RFC-822)")

    # Processes
    draw_proc(0.35, 0.75, 0.08, "1.0", "Static MIME\nDecomposer")
    draw_proc(0.60, 0.75, 0.08, "2.0", "5-Vector Signal\nExtractor")
    draw_proc(0.85, 0.75, 0.08, "3.0", "ML & SHAP\nAttribution")

    draw_proc(0.48, 0.28, 0.08, "4.0", "Risk Fusion\nEngine")
    draw_proc(0.80, 0.28, 0.08, "5.0", "ReportLab PDF\nGenerator")

    # Stores
    draw_store(0.48, 0.50, 0.24, 0.08, "D1: TF-IDF & Scaler Artifacts")
    draw_store(0.76, 0.50, 0.20, 0.08, "D2: SQLite Audit Ledger")

    # Data Flow Connections
    def arrow(x1, y1, x2, y2, label=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5))
        if label:
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            ax.text(mx, my + 0.02, label, fontsize=7.2, color="#0f172a", ha='center', va='bottom',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor="#cbd5e1", lw=0.5))

    arrow(0.20, 0.75, 0.27, 0.75, "Raw Email Payload")
    arrow(0.20, 0.31, 0.29, 0.69, "Ingest File Stream")
    arrow(0.43, 0.75, 0.52, 0.75, "Parsed Headers & Body")
    arrow(0.68, 0.75, 0.77, 0.75, "Extracted Features")
    arrow(0.60, 0.67, 0.60, 0.58, "Model Weights")
    
    arrow(0.85, 0.67, 0.54, 0.33, "ML Proba & SHAP Values")
    arrow(0.56, 0.28, 0.72, 0.28, "Composite Score (0-100)")
    arrow(0.50, 0.36, 0.76, 0.50, "Persist Record")
    arrow(0.80, 0.36, 0.84, 0.50, "Audit Data")
    arrow(0.80, 0.20, 0.12, 0.20, "Forensic PDF Download")

    path = os.path.join(OUTPUT_DIR, "fig3_data_flow_diagram.png")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Generated {path}")

# =====================================================================
# FIGURE 4: MAJOR FUNCTIONAL MODULES DECOMPOSITION
# =====================================================================
def generate_fig4_modules():
    fig, ax = style_fig("Figure 4: Major Modules Decomposition of PhishGuard SOC")

    modules = [
        ("Module 1: Static MIME Parser", 
         ["RFC-822 Header Decomposition", "MIME Boundary Unwrapping", "HTML Script/Style Stripping", "Passive Zero-Outbound Guard"],
         "#3b82f6"),
        ("Module 2: 5-Vector Risk Engine", 
         ["30% ML Probability Weight", "20% URL Entropy & TLD Heuristics", "20% SPF/DKIM/DMARC Spoofing", "15% Social + 15% Attachment Fingerprinting"],
         "#8b5cf6"),
        ("Module 3: Explainable AI (SHAP)", 
         ["LinearExplainer Game-Theoretic Log-Odds", "Top Positive Phishing Drivers (+)", "Top Negative Benign Anchors (-)", "Deterministic Natural Language Rationale"],
         "#10b981"),
        ("Module 4: In-Body XAI Highlighter", 
         ["Interactive DOM Token Matching", "Color-Coded Red/Green Word Badges", "Dynamic Hover Tooltips (Shapley Value)", "Plain vs Raw RFC-822 Source View"],
         "#06b6d4"),
        ("Module 5: Novelty Research Modules", 
         ["Module A: Stylometric AI Authorship", "Lexical Diversity (TTR & Hapax Legomena)", "Module B: Denis & Meurant Adversarial Engine", "Trigger Removal Robustness Benchmark"],
         "#f59e0b"),
        ("Module 6: Cyber-SOC Dashboard & PDF", 
         ["Animated Circular Threat Gauge (0-100)", "Dual Presets & User Tested Mails Tabs", "SQLite Investigation Audit Ledger", "Cryptographic ReportLab PDF Generator"],
         "#ef4444")
    ]

    for i, (m_title, m_items, m_color) in enumerate(modules):
        col = i % 3
        row = i // 3
        x = 0.04 + col * 0.32
        y = 0.50 if row == 0 else 0.08
        w = 0.28
        h = 0.36

        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                      facecolor="#ffffff", edgecolor=m_color, linewidth=2, zorder=2)
        ax.add_patch(rect)
        
        # Header banner
        hdr = patches.Rectangle((x, y + h - 0.07), w, 0.07, facecolor=m_color, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.035, m_title, fontsize=8.2, fontweight='bold', color="#ffffff",
                ha='center', va='center', zorder=4)

        y_text = y + h - 0.11
        for it in m_items:
            ax.text(x + 0.02, y_text, f"• {it}", fontsize=7.6, color="#1e293b", va='top', zorder=4)
            y_text -= 0.055

    path = os.path.join(OUTPUT_DIR, "fig4_major_modules.png")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Generated {path}")

# =====================================================================
# FIGURE 5: UML USE CASE DIAGRAM
# =====================================================================
def generate_fig5_use_case():
    fig, ax = style_fig("Figure 5: UML Use Case Diagram (System Actors & Functional Boundaries)")

    # System boundary
    sys_box = patches.Rectangle((0.26, 0.05), 0.48, 0.88, facecolor="#f8fafc", edgecolor="#475569",
                                linewidth=2, linestyle="--", zorder=1)
    ax.add_patch(sys_box)
    ax.text(0.50, 0.90, "PhishGuard SOC Analytical Boundary", fontsize=10, fontweight='bold',
            color="#334155", ha='center', va='center', zorder=2)

    # Actors
    def draw_actor(x, y, name):
        circle = patches.Circle((x, y + 0.04), 0.025, facecolor="#ffffff", edgecolor="#0f172a", lw=1.5, zorder=3)
        ax.add_patch(circle)
        ax.plot([x, x], [y + 0.015, y - 0.03], color="#0f172a", lw=1.5, zorder=3)
        ax.plot([x - 0.025, x + 0.025], [y, y], color="#0f172a", lw=1.5, zorder=3)
        ax.plot([x, x - 0.02], [y - 0.03, y - 0.07], color="#0f172a", lw=1.5, zorder=3)
        ax.plot([x, x + 0.02], [y - 0.03, y - 0.07], color="#0f172a", lw=1.5, zorder=3)
        ax.text(x, y - 0.09, name, fontsize=8, fontweight='bold', color="#0f172a", ha='center', va='top')

    draw_actor(0.10, 0.75, "SOC Analyst (Tier-1)")
    draw_actor(0.10, 0.35, "Incident Responder")
    draw_actor(0.88, 0.65, "Security Auditor")
    draw_actor(0.88, 0.25, "SQLite Audit DB")

    use_cases = [
        (0.50, 0.81, "Ingest Raw RFC-822 / .EML File"),
        (0.50, 0.70, "Validate SPF / DKIM / DMARC Authentication"),
        (0.50, 0.59, "Scan Static URLs for Entropy & Raw IPs"),
        (0.50, 0.48, "Examine In-Body SHAP Token Highlights"),
        (0.50, 0.37, "Evaluate Stylometric AI Authorship (Mod A)"),
        (0.50, 0.26, "Run Adversarial Perturbation Tests (Mod B)"),
        (0.50, 0.15, "Export Tamper-Evident Forensic PDF")
    ]

    for ux, uy, utext in use_cases:
        ellipse = patches.Ellipse((ux, uy), 0.38, 0.075, facecolor="#ffffff", edgecolor="#2563eb",
                                  linewidth=1.8, zorder=3)
        ax.add_patch(ellipse)
        ax.text(ux, uy, utext, fontsize=7.8, fontweight='bold', color="#1e3a8a", ha='center', va='center', zorder=4)

    def line(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color="#64748b", lw=1.2, zorder=2)

    line(0.15, 0.75, 0.31, 0.81)
    line(0.15, 0.75, 0.31, 0.70)
    line(0.15, 0.75, 0.31, 0.59)
    line(0.15, 0.75, 0.31, 0.48)

    line(0.15, 0.35, 0.31, 0.48)
    line(0.15, 0.35, 0.31, 0.37)
    line(0.15, 0.35, 0.31, 0.15)

    line(0.82, 0.65, 0.69, 0.26)
    line(0.82, 0.65, 0.69, 0.15)
    line(0.82, 0.25, 0.69, 0.15)
    line(0.82, 0.25, 0.69, 0.81)

    path = os.path.join(OUTPUT_DIR, "fig5_use_case_diagram.png")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Generated {path}")

# =====================================================================
# FIGURE 6: UML SEQUENCE DIAGRAM
# =====================================================================
def generate_fig6_sequence():
    fig, ax = style_fig("Figure 6: UML Sequence Diagram (Email Ingestion to XAI DOM Highlighting & PDF Output)")

    lifelines = [
        ("SOC Analyst (UI)", 0.10),
        ("FastAPI Gateway", 0.28),
        ("Static MIME Parser", 0.46),
        ("ML & SHAP Core", 0.64),
        ("Risk Engine", 0.80),
        ("SQLite DB", 0.94)
    ]

    for name, x in lifelines:
        box = patches.Rectangle((x - 0.08, 0.86), 0.16, 0.06, facecolor="#e2e8f0", edgecolor="#334155", lw=1.5, zorder=2)
        ax.add_patch(box)
        ax.text(x, 0.89, name, fontsize=7.5, fontweight='bold', color="#0f172a", ha='center', va='center', zorder=3)
        ax.plot([x, x], [0.86, 0.06], color="#94a3b8", linestyle="--", lw=1.2, zorder=1)

    messages = [
        (0.80, 0.10, 0.28, "1: POST /api/analyze (raw_email)"),
        (0.72, 0.28, 0.46, "2: parse_email(raw_input, zero_fetch)"),
        (0.64, 0.46, 0.28, "3: return parsed_envelope (headers, body)"),
        (0.56, 0.28, 0.64, "4: predict_proba() & explain_text()"),
        (0.48, 0.64, 0.64, "5: LinearExplainer(Shapley log-odds)"),
        (0.40, 0.64, 0.28, "6: return ML proba & feature weights"),
        (0.32, 0.28, 0.80, "7: compute_risk(5 vectors + penalties)"),
        (0.24, 0.80, 0.94, "8: persist IncidentRecord(UUID)"),
        (0.16, 0.80, 0.28, "9: return CompositeRisk (Score: 77.1)"),
        (0.08, 0.28, 0.10, "10: Render Animated HUD & In-Body XAI")
    ]

    for y, x1, x2, msg in messages:
        if x1 == x2: # self call
            ax.annotate("", xy=(x1, y - 0.03), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.4, connectionstyle="arc3,rad=-0.4"))
            ax.text(x1 + 0.03, y - 0.015, msg, fontsize=7, color="#1e3a8a", va='center')
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color="#1e293b", lw=1.3))
            ax.text((x1+x2)/2, y + 0.015, msg, fontsize=7, color="#0f172a", ha='center', va='bottom')

    path = os.path.join(OUTPUT_DIR, "fig6_sequence_diagram.png")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Generated {path}")

# =====================================================================
# FIGURE 7: UML CLASS DIAGRAM
# =====================================================================
def generate_fig7_class():
    fig, ax = style_fig("Figure 7: UML Class Diagram (Domain Models & Relational Entities)")

    def draw_class(x, y, w, h, class_name, attributes, methods, color="#4338ca"):
        ax.add_patch(patches.Rectangle((x, y + h - 0.06), w, 0.06, facecolor=color, edgecolor="#1e1b4b", lw=1.5, zorder=2))
        ax.text(x + w/2, y + h - 0.03, class_name, fontsize=8.2, fontweight='bold', color="#ffffff", ha='center', va='center', zorder=3)
        ax.add_patch(patches.Rectangle((x, y), w, h - 0.06, facecolor="#ffffff", edgecolor="#1e1b4b", lw=1.5, zorder=2))
        
        y_cur = y + h - 0.09
        for a in attributes:
            ax.text(x + 0.015, y_cur, f"- {a}", fontsize=7, color="#1e293b", va='top', zorder=3)
            y_cur -= 0.038
        
        ax.plot([x, x + w], [y_cur - 0.01, y_cur - 0.01], color="#cbd5e1", lw=1, zorder=3)
        y_cur -= 0.03
        for m in methods:
            ax.text(x + 0.015, y_cur, f"+ {m}()", fontsize=7, color="#047857", va='top', zorder=3)
            y_cur -= 0.038

    draw_class(0.04, 0.50, 0.28, 0.40, "ParsedEmail",
               ["headers: HeaderInfo", "body_plain: String", "body_html: String", "urls: List[String]", "attachments: List[Attach]"],
               ["extractURLs", "sanitizeText", "computeSHA256"], "#3b82f6")

    draw_class(0.36, 0.50, 0.28, 0.40, "TriageService",
               ["ml_service: MLService", "explainer: XAIService", "risk_engine: RiskEngine", "authorship: AuthorService"],
               ["analyzeEmail", "extractSignals", "generatePDF"], "#8b5cf6")

    draw_class(0.68, 0.50, 0.28, 0.40, "RiskEngine",
               ["weight_ml: 30%", "weight_url: 20%", "weight_headers: 20%", "weight_social: 15%", "weight_attach: 15%"],
               ["computeRisk", "applyPenalties", "getVerdict"], "#059669")

    draw_class(0.04, 0.05, 0.28, 0.40, "SHAPExplainer",
               ["explainer: LinearExplainer", "feature_names: List[Str]", "max_features: 645"],
               ["explainText", "getTopPhishFeatures", "synthesizeRationale"], "#d97706")

    draw_class(0.36, 0.05, 0.28, 0.40, "AnalysisRecord (ORM)",
               ["id: String (UUID)", "risk_score: Float", "severity: String", "ml_probability: Float", "created_at: Datetime"],
               ["saveToSQLite", "queryHistory", "exportJSON"], "#dc2626")

    draw_class(0.68, 0.05, 0.28, 0.40, "AuthorshipService",
               ["classifier: LogisticReg", "scaler: StandardScaler", "stylometric_indicators: Dict"],
               ["extractStylometrics", "predictAILikelihood", "getHapaxLegomena"], "#0d9488")

    path = os.path.join(OUTPUT_DIR, "fig7_class_diagram.png")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Generated {path}")

# =====================================================================
# FIGURE 8: UML ACTIVITY DIAGRAM
# =====================================================================
def generate_fig8_activity():
    fig, ax = style_fig("Figure 8: UML Activity Diagram (End-to-End Decision Logic & Branching)")

    def draw_state(x, y, w, h, text, bg="#dbeafe", border="#1d4ed8"):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                      facecolor=bg, edgecolor=border, lw=1.8, zorder=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, fontsize=7.5, fontweight='bold', color="#1e3a8a",
                ha='center', va='center', zorder=3)

    def draw_decision(x, y, size, text):
        diamond = patches.Polygon([[x, y + size/2], [x + size/2, y], [x, y - size/2], [x - size/2, y]],
                                  facecolor="#fef3c7", edgecolor="#d97706", lw=1.8, zorder=2)
        ax.add_patch(diamond)
        ax.text(x, y, text, fontsize=7, fontweight='bold', color="#78350f", ha='center', va='center', zorder=3)

    # Start Node
    ax.add_patch(patches.Circle((0.10, 0.80), 0.025, facecolor="#0f172a", zorder=3))
    ax.text(0.10, 0.85, "Start", fontsize=8.5, fontweight='bold', ha='center')

    draw_state(0.18, 0.76, 0.16, 0.08, "Ingest RFC-822\nRaw Message")
    draw_decision(0.42, 0.80, 0.10, "Valid MIME\nEnvelope?")
    draw_state(0.55, 0.76, 0.18, 0.08, "Passive 5-Vector\nSignal Extraction")
    draw_decision(0.82, 0.80, 0.10, "Spoofed SPF\nOr Raw IP?")

    draw_state(0.82, 0.50, 0.15, 0.08, "Apply Severe\nPenalty (+20 pts)")
    draw_state(0.55, 0.50, 0.18, 0.08, "Calculate SHAP\nShapley Values")
    draw_state(0.28, 0.50, 0.18, 0.08, "Synthesize Weighted\nRisk Score (0-100)")

    draw_decision(0.15, 0.50, 0.10, "Composite\nScore >= 50?")
    draw_state(0.10, 0.25, 0.20, 0.08, "VERDICT: PHISHING\n(Quarantine & Block)")
    draw_decision(0.40, 0.29, 0.10, "Score >= 25?")
    draw_state(0.35, 0.12, 0.20, 0.08, "VERDICT: SUSPICIOUS\n(Tag External Warning)")
    draw_state(0.65, 0.12, 0.20, 0.08, "VERDICT: LEGITIMATE\n(Deliver to Inbox)")

    # Arrows
    def arrow(x1, y1, x2, y2, lbl=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#334155", lw=1.3))
        if lbl:
            ax.text((x1+x2)/2, (y1+y2)/2 + 0.02, lbl, fontsize=7, color="#0f172a", ha='center')

    arrow(0.125, 0.80, 0.18, 0.80)
    arrow(0.34, 0.80, 0.37, 0.80)
    arrow(0.47, 0.80, 0.55, 0.80, "Yes")
    arrow(0.73, 0.80, 0.77, 0.80)
    arrow(0.82, 0.75, 0.82, 0.58, "Yes")
    arrow(0.82, 0.85, 0.70, 0.58, "No")

    arrow(0.82, 0.50, 0.73, 0.50)
    arrow(0.55, 0.50, 0.46, 0.50)
    arrow(0.28, 0.50, 0.20, 0.50)

    arrow(0.15, 0.45, 0.15, 0.33, "Yes")
    arrow(0.20, 0.50, 0.35, 0.29, "No")
    arrow(0.40, 0.24, 0.40, 0.20, "Yes")
    arrow(0.45, 0.29, 0.65, 0.16, "No (<25)")

    path = os.path.join(OUTPUT_DIR, "fig8_activity_diagram.png")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Generated {path}")

# =====================================================================
# FIGURE 9: UML DEPLOYMENT DIAGRAM
# =====================================================================
def generate_fig9_deployment():
    fig, ax = style_fig("Figure 9: UML Deployment Diagram (Physical Node Mapping & Topology)")

    def draw_node(x, y, w, h, name, ip_port, components, color="#3b82f6"):
        rect = patches.Rectangle((x, y), w, h, facecolor="#ffffff", edgecolor=color, lw=2, zorder=2)
        ax.add_patch(rect)
        ax.add_patch(patches.Rectangle((x, y + h - 0.07), w, 0.07, facecolor=color, zorder=3))
        ax.text(x + w/2, y + h - 0.035, f"<<device>> {name}\n{ip_port}", fontsize=7.5, fontweight='bold',
                color="#ffffff", ha='center', va='center', zorder=4)

        y_c = y + h - 0.11
        for comp in components:
            cbox = patches.Rectangle((x + 0.02, y_c - 0.045), w - 0.04, 0.045, facecolor="#f1f5f9",
                                     edgecolor="#cbd5e1", lw=1, zorder=3)
            ax.add_patch(cbox)
            ax.text(x + w/2, y_c - 0.022, f"<<component>> {comp}", fontsize=6.8, color="#1e293b",
                    ha='center', va='center', zorder=4)
            y_c -= 0.06

    draw_node(0.04, 0.20, 0.26, 0.60, "SOC Client Workstation", "Port: 5174", [
        "React 18 SPA (Vite 5)",
        "Cyber-SOC Radar HUD",
        "In-Body XAI Highlighter",
        "Axios REST Client"
    ], "#2563eb")

    draw_node(0.37, 0.20, 0.26, 0.60, "Security Server", "Port: 8001", [
        "FastAPI Async Gateway",
        "Uvicorn ASGI Engine",
        "Static MIME Decomposer",
        "5-Vector Risk Engine",
        "ReportLab PDF Compiler"
    ], "#10b981")

    draw_node(0.70, 0.52, 0.26, 0.38, "In-Process AI Worker", "Local Python RAM", [
        "TF-IDF Vectorizer (645 n-grams)",
        "LogisticRegression Classifier",
        "SHAP LinearExplainer",
        "Stylometric Authorship Core"
    ], "#8b5cf6")

    draw_node(0.70, 0.08, 0.26, 0.38, "Persistence Storage", "SQLite / Filesystem", [
        "phishing_risk_analyzer.db",
        "AnalysisRecord Tables",
        "reports/generated/*.pdf",
        "models/*.pkl Artifacts"
    ], "#f59e0b")

    # Connectors
    ax.annotate("", xy=(0.37, 0.50), xytext=(0.30, 0.50),
                arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=2))
    ax.text(0.335, 0.53, "HTTP / REST\nJSON Payloads", fontsize=7.2, color="#0f172a", ha='center')

    ax.annotate("", xy=(0.70, 0.68), xytext=(0.63, 0.68),
                arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=2))
    ax.text(0.665, 0.71, "Python C-API\nIn-Process IPC", fontsize=7.2, color="#0f172a", ha='center')

    ax.annotate("", xy=(0.70, 0.27), xytext=(0.63, 0.27),
                arrowprops=dict(arrowstyle="<->", color="#0f172a", lw=2))
    ax.text(0.665, 0.30, "SQLAlchemy Pool\nSQLite Native I/O", fontsize=7.2, color="#0f172a", ha='center')

    path = os.path.join(OUTPUT_DIR, "fig9_deployment_diagram.png")
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Generated {path}")

if __name__ == "__main__":
    generate_fig1_end_to_end()
    generate_fig2_workflow()
    generate_fig3_dfd()
    generate_fig4_modules()
    generate_fig5_use_case()
    generate_fig6_sequence()
    generate_fig7_class()
    generate_fig8_activity()
    generate_fig9_deployment()
    print("\n[SUCCESS] All 9 publication diagrams generated successfully in reports/figures/!")
