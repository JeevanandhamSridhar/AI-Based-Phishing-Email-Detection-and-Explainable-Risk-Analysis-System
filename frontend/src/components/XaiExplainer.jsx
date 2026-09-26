import React, { useState } from 'react';
import { Sparkles, TrendingUp, TrendingDown, HelpCircle, ShieldAlert, ArrowRight, Info, Search } from 'lucide-react';

export default function XaiExplainer({ explainability = {}, onViewInBody }) {
  const {
    method = 'SHAP (LinearExplainer)',
    human_readable_summary = 'No textual explanation generated.',
    top_phishing_features = [],
    top_legitimate_features = [],
    caveat = 'Feature attribution reflects local token influence on classifier decision, not legal proof.',
  } = explainability;

  const [filterQuery, setFilterQuery] = useState('');

  // Find max absolute importance for normalization of visual bar widths
  const allFeatures = [...top_phishing_features, ...top_legitimate_features];
  const maxScore = Math.max(
    ...allFeatures.map(f => Math.abs(Number(f.importance || f.attribution || f.weight || 0.1))),
    0.5
  );

  const filteredPhish = top_phishing_features.filter(f => 
    (f.feature || f.token || f.word || '').toLowerCase().includes(filterQuery.toLowerCase())
  );

  const filteredLegit = top_legitimate_features.filter(f => 
    (f.feature || f.token || f.word || '').toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800/90 shadow-2xl relative overflow-hidden">
      {/* Top Gradient Highlight */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500/50 via-blue-500/50 to-indigo-500/50" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
            <Sparkles className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-sm font-['Outfit']">
              Explainable AI (XAI) Attribution
            </h3>
            <p className="text-[11px] text-slate-400 font-mono">
              Local Feature Shapley Values & Attribution
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono px-2.5 py-1 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            {method}
          </span>
          {onViewInBody && (
            <button
              onClick={onViewInBody}
              className="px-3 py-1 rounded-md bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 hover:text-white border border-blue-500/40 text-xs font-mono flex items-center gap-1.5 transition-all shadow-sm"
              title="Jump to In-Body Token Highlighter"
            >
              <span>Inspect in Body</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Natural Language Triage Synthesis */}
      <div className="mb-5 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 relative">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
            <HelpCircle className="w-4 h-4 text-blue-400" />
            <span>Natural Language Triage Rationale</span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">Rule-Template Synthesizer</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-900/50 p-3 rounded-lg border border-slate-800/50">
          {human_readable_summary}
        </p>
      </div>

      {/* Dual Attribution Columns with Dynamic Bars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
        {/* Phishing Positive Influence */}
        <div className="p-4 rounded-xl bg-red-950/20 border border-red-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-red-300">
              <TrendingUp className="w-4 h-4 text-red-400" />
              <span>Phishing Risk Drivers (+ log-odds)</span>
            </div>
            <span className="text-[10px] font-mono text-red-400/80">
              {filteredPhish.length} features
            </span>
          </div>

          {filteredPhish.length > 0 ? (
            <div className="space-y-2.5">
              {filteredPhish.map((item, idx) => {
                const token = item.feature || item.token || item.word || 'token';
                const score = Number(item.importance || item.attribution || item.weight || 0);
                const pct = Math.min(100, Math.max(10, Math.round((Math.abs(score) / maxScore) * 100)));

                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-red-200 font-semibold px-1.5 py-0.5 rounded bg-red-950/60 border border-red-800/40">
                        "{token}"
                      </span>
                      <span className="text-red-400 font-bold">
                        +{score.toFixed(3)}
                      </span>
                    </div>
                    {/* Visual Bar */}
                    <div className="w-full h-1.5 bg-slate-800/80 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-red-600 to-rose-400 rounded-full transition-all duration-700"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic py-4 text-center">
              No strong phishing tokens detected.
            </p>
          )}
        </div>

        {/* Legitimate Negative Influence */}
        <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/40 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-300">
              <TrendingDown className="w-4 h-4 text-emerald-400" />
              <span>Benign Anchors (- log-odds)</span>
            </div>
            <span className="text-[10px] font-mono text-emerald-400/80">
              {filteredLegit.length} features
            </span>
          </div>

          {filteredLegit.length > 0 ? (
            <div className="space-y-2.5">
              {filteredLegit.map((item, idx) => {
                const token = item.feature || item.token || item.word || 'token';
                const score = Number(item.importance || item.attribution || item.weight || 0);
                const pct = Math.min(100, Math.max(10, Math.round((Math.abs(score) / maxScore) * 100)));

                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-emerald-200 font-semibold px-1.5 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/40">
                        "{token}"
                      </span>
                      <span className="text-emerald-400 font-bold">
                        {score.toFixed(3)}
                      </span>
                    </div>
                    {/* Visual Bar */}
                    <div className="w-full h-1.5 bg-slate-800/80 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-600 to-teal-400 rounded-full transition-all duration-700"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic py-4 text-center">
              No strong legitimate anchors detected.
            </p>
          )}
        </div>
      </div>

      {/* Defensive Boundary Caveat */}
      <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-start gap-2.5">
        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <p className="text-[11px] text-slate-400 leading-normal">
          <strong className="text-slate-300 font-mono">Academic Caveat: </strong>
          {caveat}
        </p>
      </div>
    </div>
  );
}
