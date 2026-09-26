import React from 'react';
import { Bot, User, Brain, AlertCircle, BarChart3 } from 'lucide-react';

export default function AuthorshipCard({ aiAuthorship = {} }) {
  const {
    ai_generated_likelihood = 0.0,
    classification = 'Human-Authored',
    stylometric_indicators = {},
    caveat = 'Model-based indicator, not proof of AI authorship.',
  } = aiAuthorship;

  const rawLikelihood = Number(ai_generated_likelihood || 0);
  const pct = rawLikelihood <= 1.0 ? Math.round(rawLikelihood * 100) : Math.round(rawLikelihood);
  const isAI = pct >= 50;

  return (
    <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-purple-400" />
          <h3 className="font-semibold text-slate-200 text-sm font-['Outfit']">
            Module A: AI Authorship Indicator
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
          Research Novelty
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-5 mb-5 p-4 rounded-xl bg-slate-800/50 border border-slate-700/60">
        {/* Probability readout */}
        <div className="flex flex-col items-center justify-center p-3 rounded-xl bg-slate-900/80 border border-slate-700/80 w-28 shrink-0">
          <span className="text-3xl font-extrabold font-['Outfit'] text-purple-400">
            {pct}%
          </span>
          <span className="text-[10px] uppercase font-mono text-slate-400 tracking-wider">
            AI Likelihood
          </span>
        </div>

        {/* Classification Verdict */}
        <div className="flex-1 text-center sm:text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs font-semibold font-mono mb-2 border bg-purple-950/40 border-purple-800/60 text-purple-200">
            {isAI ? <Bot className="w-3.5 h-3.5 text-purple-400" /> : <User className="w-3.5 h-3.5 text-slate-400" />}
            <span>Verdict: {classification}</span>
          </div>
          <p className="text-xs text-slate-300">
            {isAI 
              ? 'Stylometric profile exhibits high uniform sentence rhythm, lower hapax legomena, and synthetic token patterns typical of LLM generators.' 
              : 'Stylometric profile exhibits natural lexical variance, human punctuation irregularities, and typical organic phrasing.'}
          </p>
        </div>
      </div>

      {/* Stylometric Features List */}
      {stylometric_indicators && Object.keys(stylometric_indicators).length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold text-slate-400 font-mono">
            <BarChart3 className="w-3.5 h-3.5 text-purple-400" />
            <span>Extracted Stylometric Markers</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {Object.entries(stylometric_indicators).map(([key, val]) => (
              <div key={key} className="p-2 rounded-lg bg-slate-800/40 border border-slate-700/40">
                <span className="text-[10px] text-slate-400 block truncate">{key.replace(/_/g, ' ')}</span>
                <span className="text-xs font-mono font-semibold text-slate-200">
                  {typeof val === 'number' ? val.toFixed(3) : String(val)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Caveat */}
      <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-700/40 flex items-start gap-2">
        <AlertCircle className="w-3.5 h-3.5 text-purple-400 shrink-0 mt-0.5" />
        <p className="text-[11px] text-slate-400">
          <strong className="text-slate-300 font-mono">Academic Disclosure: </strong>
          {caveat} Evaluated across multiple LLM generators with documented cross-model performance drop.
        </p>
      </div>
    </div>
  );
}
