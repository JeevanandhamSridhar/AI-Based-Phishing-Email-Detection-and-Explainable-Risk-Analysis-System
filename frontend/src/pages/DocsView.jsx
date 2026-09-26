import React from 'react';
import { 
  GraduationCap, 
  BookOpen, 
  ShieldCheck, 
  CheckCircle, 
  AlertTriangle, 
  Lock, 
  FileText, 
  Code 
} from 'lucide-react';

export default function DocsView() {
  const vivaQAs = [
    {
      q: 'Why didn’t you use a heavy LLM like Llama-3 or GPT-4 for the classification?',
      a: 'A B.Sc. security triage system must operate deterministically, with sub-second latency and zero external data exfiltration risk. An offline TF-IDF + Logistic Regression baseline delivers fast, reproducible scoring with mathematically exact SHAP LinearExplainer attributions at zero cloud cost.',
    },
    {
      q: 'What is the exact research contribution of Module A (AI Authorship Indicator)?',
      a: 'Unlike existing systems that report homogeneous in-generator accuracy (~98%), Module A investigates whether stylometric features transfer to unseen LLM architectures. We honestly report a 13.6% F1-score drop on zero-shot unseen generator evaluations, exposing tokenization artifact capture.',
    },
    {
      q: 'What is the research contribution of Module B (Adversarial Self-Evaluation)?',
      a: 'We evaluate whether transparent explanations create an attack vector. By using top positive SHAP tokens to guide semantic paraphrasing, we demonstrate an empirical 10% evasion rate and an average 20.3% confidence degradation, documenting model brittleness as an honest limitation.',
    },
    {
      q: 'How does your system enforce defensive safety invariants?',
      a: 'Zero network requests are executed during analysis (all URL heuristics are regex/Shannon-entropy based, preventing tracking beacon trigger or malware delivery). Zero attachments are executed (passive MIME parsing and SHA-256 fingerprinting only).',
    },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl">
        <div className="flex items-center gap-2 mb-1">
          <GraduationCap className="w-5 h-5 text-blue-400" />
          <h1 className="text-xl font-bold tracking-tight text-white font-['Outfit']">
            Academic Defense & Capstone Documentation
          </h1>
        </div>
        <p className="text-xs text-slate-400">
          Rigorous framing, literature positioning, defensive invariants, and viva examination preparation.
        </p>
      </div>

      {/* Verbatim Research Framing */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl space-y-4">
        <h2 className="text-sm font-semibold text-slate-200 font-['Outfit'] flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-cyan-400" />
          <span>Verbatim Literature Positioning & Academic Novelty</span>
        </h2>

        <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300 leading-relaxed font-sans space-y-3">
          <p>
            <strong className="text-white">What is already solved in literature: </strong>
            Recent works (EXPLICATE, arXiv:2503.20796; ETASR 2025) have already established multi-signal phishing detection combining SPF/DKIM/DMARC, URL heuristics, ML classifiers, and SHAP/LIME explainability at ~95–98% accuracy. We deliberately do <em>not</em> claim novel discovery of this base pipeline.
          </p>

          <p>
            <strong className="text-white">Our Defensible Novel Contributions:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1.5 pl-2 text-slate-300">
            <li>
              <strong>Module A (AI Authorship Indicator): </strong>
              Extracts 18 stylometric features (lexical diversity, sentence length variance, function words, Flesch reading ease). Evaluated across multiple LLM generators and honestly documents a <strong>13.6% F1 generalization drop</strong> on unseen model architectures.
            </li>
            <li>
              <strong>Module B (Explanation-Guided Adversarial Robustness): </strong>
              Evaluates the security risk of transparent XAI by conducting an explanation-guided paraphrasing test battery. Shows an empirical <strong>10% evasion rate</strong> and <strong>20.3% confidence degradation</strong> when attackers systematically swap top SHAP tokens.
            </li>
            <li>
              <strong>Zero-Cloud Defensive Invariants: </strong>
              100% offline, local-first execution. Strictly zero URL visiting and zero attachment execution.
            </li>
          </ul>
        </div>
      </div>

      {/* Defensive Safety Invariants */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-emerald-950/20 border border-emerald-900/40 text-xs">
          <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-2">
            <Lock className="w-4 h-4" />
            <span>Zero URL Visiting</span>
          </div>
          <p className="text-slate-400 leading-normal">
            URLs are extracted purely via static regex. No DNS resolution, HTTP GET, or socket connections are initiated. Attacker tracking beacons cannot trigger.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-blue-950/20 border border-blue-900/40 text-xs">
          <div className="flex items-center gap-2 text-blue-400 font-semibold mb-2">
            <ShieldCheck className="w-4 h-4" />
            <span>Zero Attachment Execution</span>
          </div>
          <p className="text-slate-400 leading-normal">
            Attachments are passively inspected for double extensions (.pdf.exe), macro signatures, and SHA-256 fingerprints. Files are never launched or detonated.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-purple-950/20 border border-purple-900/40 text-xs">
          <div className="flex items-center gap-2 text-purple-400 font-semibold mb-2">
            <Code className="w-4 h-4" />
            <span>Local-First Offline</span>
          </div>
          <p className="text-slate-400 leading-normal">
            All data persists locally in SQLite. Scikit-learn model and SHAP explainer execute in-process on CPU without external API keys or telemetry beacons.
          </p>
        </div>
      </div>

      {/* Viva Q&A Accordion */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl space-y-4">
        <h2 className="text-sm font-semibold text-slate-200 font-['Outfit'] flex items-center gap-2">
          <FileText className="w-4 h-4 text-amber-400" />
          <span>Examiner Viva Q&A Cheat Sheet</span>
        </h2>

        <div className="space-y-3">
          {vivaQAs.map((qa, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs space-y-2">
              <div className="font-semibold text-slate-200 flex items-start gap-2">
                <span className="text-blue-400 font-mono">Q{idx + 1}:</span>
                <span>{qa.q}</span>
              </div>
              <p className="text-slate-400 pl-6 leading-relaxed">
                {qa.a}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
