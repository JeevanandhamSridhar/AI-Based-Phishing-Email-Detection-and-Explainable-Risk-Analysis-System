import React from 'react';
import { Sparkles, TrendingUp, TrendingDown, HelpCircle, ShieldAlert } from 'lucide-react';

export default function XaiExplainer({ explainability = {} }) {
  const {
    method = 'SHAP (LinearExplainer)',
    human_readable_summary = 'No textual explanation generated.',
    top_phishing_features = [],
    top_legitimate_features = [],
    caveat = 'Feature attribution reflects local token influence on classifier decision, not legal proof.',
  } = explainability;

  return (
    <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <h3 className="font-semibold text-slate-200 text-sm font-['Outfit']">
            Explainable AI (XAI) Attribution
          </h3>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          {method}
        </span>
      </div>

      {/* Plain English Synthesis */}
      <div className="mb-5 p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
        <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-300">
          <HelpCircle className="w-3.5 h-3.5 text-blue-400" />
          <span>Natural Language Triage Rationale</span>
        </div>
        <p className="text-xs text-slate-200 leading-relaxed font-sans">
          {human_readable_summary}
        </p>
      </div>

      {/* Feature Attribution Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Top Phishing Features (+ Influence) */}
        <div className="p-3.5 rounded-xl bg-red-950/20 border border-red-900/40">
          <div className="flex items-center gap-1.5 mb-2.5 text-xs font-semibold text-red-400">
            <TrendingUp className="w-3.5 h-3.5 text-red-400" />
            <span>Phishing Indicators (+ Risk)</span>
          </div>

          {top_phishing_features.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {top_phishing_features.map((item, idx) => (
                <div
                  key={idx}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-red-900/30 border border-red-700/40 text-red-200 text-xs font-mono"
                >
                  <span className="font-semibold">{item.feature || item.token || item.word}</span>
                  <span className="text-[10px] text-red-400 bg-red-950/60 px-1 py-0.5 rounded">
                    +{Number(item.importance || item.attribution || item.weight || 0).toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No strong phishing tokens detected.</p>
          )}
        </div>

        {/* Top Legitimate Features (- Influence) */}
        <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-900/40">
          <div className="flex items-center gap-1.5 mb-2.5 text-xs font-semibold text-emerald-400">
            <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
            <span>Benign Indicators (- Risk)</span>
          </div>

          {top_legitimate_features.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {top_legitimate_features.map((item, idx) => (
                <div
                  key={idx}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-900/30 border border-emerald-700/40 text-emerald-200 text-xs font-mono"
                >
                  <span className="font-semibold">{item.feature || item.token || item.word}</span>
                  <span className="text-[10px] text-emerald-400 bg-emerald-950/60 px-1 py-0.5 rounded">
                    {Number(item.importance || item.attribution || item.weight || 0).toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No significant benign anchor tokens.</p>
          )}
        </div>
      </div>

      {/* Defensive Boundary Caveat */}
      <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-700/40 flex items-start gap-2.5">
        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <p className="text-[11px] text-slate-400 leading-normal">
          <strong className="text-slate-300 font-mono">Academic Caveat: </strong>
          {caveat}
        </p>
      </div>
    </div>
  );
}
