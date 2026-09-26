import React from 'react';
import { Bot, User, Brain, AlertCircle, BarChart3, Sparkles } from 'lucide-react';

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
    <div className="glass-panel p-6 rounded-2xl border border-slate-800/90 shadow-2xl relative overflow-hidden">
      {/* Decorative top accent */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500/50 via-fuchsia-500/50 to-pink-500/50" />

      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-purple-500/10 border border-purple-500/20">
            <Brain className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-sm font-['Outfit']">
              AI Authorship Synthesizer
            </h3>
            <p className="text-[11px] text-slate-400 font-mono">
              Module A: Stylometric Detection
            </p>
          </div>
        </div>
        <span className="text-[10px] font-mono px-2.5 py-1 rounded-md bg-purple-500/10 text-purple-300 border border-purple-500/20 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-purple-400" />
          <span>Cross-Generator Tuned</span>
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4 mb-5 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
        {/* Probability readout */}
        <div className="flex flex-col items-center justify-center p-3 rounded-xl bg-slate-900/80 border border-purple-500/20 w-28 shrink-0 shadow-lg shadow-purple-950/30">
          <span className="text-3xl font-extrabold font-['Outfit'] text-purple-300">
            {pct}%
          </span>
          <span className="text-[9px] uppercase font-mono text-purple-400/80 tracking-wider text-center mt-0.5">
            AI Likelihood
          </span>
        </div>

        {/* Classification Verdict */}
        <div className="flex-1 text-center sm:text-left space-y-1.5">
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs font-semibold font-mono border ${
            isAI 
              ? 'bg-purple-950/60 border-purple-500/40 text-purple-200' 
              : 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
          }`}>
            {isAI ? <Bot className="w-3.5 h-3.5 text-purple-400" /> : <User className="w-3.5 h-3.5 text-emerald-400" />}
            <span>Classification: {classification}</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            {isAI 
              ? 'Stylometric profile exhibits uniform syntactic length, lower hapax legomena diversity, and synthetic transition patterns typical of LLM generation.' 
              : 'Stylometric profile exhibits natural lexical variance, human punctuation irregularities, and organic semantic phrasing.'}
          </p>
        </div>
      </div>

      {/* Stylometric Features List */}
      {stylometric_indicators && Object.keys(stylometric_indicators).length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-1.5 mb-2.5 text-xs font-semibold text-slate-300 font-mono">
            <BarChart3 className="w-3.5 h-3.5 text-purple-400" />
            <span>Extracted Stylometric Markers</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {Object.entries(stylometric_indicators).map(([key, val]) => (
              <div key={key} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 block truncate font-mono uppercase">{key.replace(/_/g, ' ')}</span>
                <span className="text-xs font-mono font-semibold text-slate-200">
                  {typeof val === 'number' ? val.toFixed(3) : String(val)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Caveat */}
      <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800/60 flex items-start gap-2">
        <AlertCircle className="w-3.5 h-3.5 text-purple-400 shrink-0 mt-0.5" />
        <p className="text-[11px] text-slate-400 leading-normal">
          <strong className="text-slate-300 font-mono">Stylometric Caveat: </strong>
          {caveat} Documented cross-generator generalizability drop observed against zero-day generative prompt variants.
        </p>
      </div>
    </div>
  );
}
