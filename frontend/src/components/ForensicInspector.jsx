import React, { useState, useMemo } from 'react';
import { 
  FileText, 
  Globe, 
  Paperclip, 
  Mail, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  ShieldCheck, 
  Hash, 
  Lock,
  Sparkles,
  Copy,
  Check,
  Search,
  Eye,
  Sliders,
  ExternalLink,
  Code,
  Info
} from 'lucide-react';

export default function ForensicInspector({
  headerFindings = {},
  urlFindings = [],
  attachmentFindings = [],
  socialFindings = {},
  emailMetadata = {},
  explainability = {},
  activeTab: controlledTab,
  onTabChange,
}) {
  const [internalTab, setInternalTab] = useState('xai_body');
  const activeTab = controlledTab !== undefined ? controlledTab : internalTab;
  const setActiveTab = onTabChange || setInternalTab;

  const [copiedText, setCopiedText] = useState(false);
  const [copiedRaw, setCopiedRaw] = useState(false);
  const [showPhishingHighlights, setShowPhishingHighlights] = useState(true);
  const [showLegitHighlights, setShowLegitHighlights] = useState(true);

  const bodyText = emailMetadata.body_text || emailMetadata.body || emailMetadata.snippet || '';
  const rawEmail = emailMetadata.raw_email || '';

  // Extract tokens for XAI highlights
  const phishingTokens = useMemo(() => {
    return (explainability.top_phishing_features || []).map(f => ({
      word: (f.feature || f.token || f.word || '').toLowerCase(),
      score: Number(f.importance || f.attribution || f.weight || 0),
      type: 'phishing'
    })).filter(t => t.word.length > 1);
  }, [explainability.top_phishing_features]);

  const legitTokens = useMemo(() => {
    return (explainability.top_legitimate_features || []).map(f => ({
      word: (f.feature || f.token || f.word || '').toLowerCase(),
      score: Number(f.importance || f.attribution || f.weight || 0),
      type: 'legitimate'
    })).filter(t => t.word.length > 1);
  }, [explainability.top_legitimate_features]);

  // Map for fast lookup
  const tokenMap = useMemo(() => {
    const map = new Map();
    phishingTokens.forEach(t => map.set(t.word, t));
    legitTokens.forEach(t => map.set(t.word, t));
    return map;
  }, [phishingTokens, legitTokens]);

  const copyToClipboard = (text, setCopied) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Render highlighted text with regex tokenization
  const renderedContent = useMemo(() => {
    if (!bodyText) {
      return (
        <div className="p-8 text-center text-slate-500 font-mono text-xs">
          [NO PLAIN BODY FOUND — HEADERS ONLY EMAIL]
        </div>
      );
    }

    const wordsToMatch = [];
    if (showPhishingHighlights) wordsToMatch.push(...phishingTokens.map(t => t.word));
    if (showLegitHighlights) wordsToMatch.push(...legitTokens.map(t => t.word));

    if (wordsToMatch.length === 0) {
      return (
        <pre className="font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed select-text">
          {bodyText}
        </pre>
      );
    }

    // Escape regex characters
    const escaped = wordsToMatch
      .sort((a, b) => b.length - a.length)
      .map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

    const pattern = new RegExp(`(\\b(?:${escaped.join('|')})\\b)`, 'gi');
    const parts = bodyText.split(pattern);

    return (
      <div className="font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed select-text">
        {parts.map((part, index) => {
          const lower = part.toLowerCase();
          const match = tokenMap.get(lower);

          if (match && ((match.type === 'phishing' && showPhishingHighlights) || (match.type === 'legitimate' && showLegitHighlights))) {
            const isPhish = match.type === 'phishing';
            return (
              <span
                key={index}
                className={`relative group inline-block font-semibold px-1.5 py-0.5 rounded mx-0.5 transition-all cursor-pointer ${
                  isPhish
                    ? 'bg-red-500/25 text-red-200 border border-red-500/50 hover:bg-red-500/40 shadow-sm shadow-red-500/20'
                    : 'bg-emerald-500/25 text-emerald-200 border border-emerald-500/50 hover:bg-emerald-500/40 shadow-sm shadow-emerald-500/20'
                }`}
              >
                {part}
                {/* Tooltip on hover */}
                <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:flex flex-col items-center z-50 pointer-events-none w-48 p-2 rounded-lg bg-slate-950/95 border border-slate-700 shadow-2xl backdrop-blur-md">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                    {isPhish ? 'Phishing Feature Trigger' : 'Benign Anchor Feature'}
                  </span>
                  <span className={`text-xs font-mono font-bold mt-0.5 ${isPhish ? 'text-red-400' : 'text-emerald-400'}`}>
                    {isPhish ? `+${match.score.toFixed(3)} SHAP` : `${match.score.toFixed(3)} SHAP`}
                  </span>
                  <span className="text-[9px] text-slate-400 text-center mt-1">
                    {isPhish ? 'Increases model phishing verdict probability' : 'Anchors prediction towards legitimate'}
                  </span>
                  <span className="w-2 h-2 bg-slate-950 border-r border-b border-slate-700 rotate-45 -mb-3 mt-1"></span>
                </span>
              </span>
            );
          }

          return <span key={index}>{part}</span>;
        })}
      </div>
    );
  }, [bodyText, showPhishingHighlights, showLegitHighlights, phishingTokens, legitTokens, tokenMap]);

  const tabs = [
    { 
      id: 'xai_body', 
      label: 'Interactive In-Body XAI', 
      icon: Sparkles,
      count: phishingTokens.length + legitTokens.length > 0 ? `${phishingTokens.length + legitTokens.length} Cues` : null,
      accent: 'text-cyan-400'
    },
    { 
      id: 'headers', 
      label: 'Headers & Auth', 
      icon: Lock,
      count: headerFindings.spoofing_detected ? 'Alert' : null,
      accent: headerFindings.spoofing_detected ? 'text-red-400' : 'text-slate-400'
    },
    { 
      id: 'urls', 
      label: 'Static URLs', 
      icon: Globe,
      count: urlFindings.length,
      accent: urlFindings.length > 0 ? 'text-blue-400' : 'text-slate-400'
    },
    { 
      id: 'attachments', 
      label: 'Attachments', 
      icon: Paperclip,
      count: attachmentFindings.length,
      accent: attachmentFindings.length > 0 ? 'text-purple-400' : 'text-slate-400'
    },
    { 
      id: 'social', 
      label: 'Social Engineering', 
      icon: AlertTriangle,
      count: (socialFindings.categories_flagged || []).length || null,
      accent: (socialFindings.categories_flagged || []).length > 0 ? 'text-amber-400' : 'text-slate-400'
    },
    {
      id: 'raw_source',
      label: 'Raw RFC-822 Source',
      icon: Code,
      count: rawEmail ? 'MIME' : null,
      accent: 'text-indigo-400'
    }
  ];

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800/90 shadow-2xl relative overflow-hidden">
      {/* Decorative gradient top edge */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500/40 via-cyan-400/40 to-indigo-500/40" />

      {/* Tab Navigation Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-1.5 overflow-x-auto py-1">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            const TabIcon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-lg shadow-blue-600/30 border border-blue-400/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                }`}
              >
                <TabIcon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : tab.accent}`} />
                <span>{tab.label}</span>
                {tab.count !== null && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : 'bg-slate-800 text-slate-300 border border-slate-700/60'
                    }`}
                  >
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
        <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20 hidden sm:inline-flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
          Zero-Interaction Sandbox
        </span>
      </div>

      {/* TAB 0: INTERACTIVE IN-BODY XAI HIGHLIGHTER */}
      {activeTab === 'xai_body' && (
        <div className="space-y-4">
          {/* Informative Explanation of Clean Extracted Text */}
          <div className="p-3 rounded-xl bg-blue-950/20 border border-blue-900/40 flex items-start gap-2.5 text-xs text-slate-300">
            <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-cyan-300 block">Parsed Semantic Message Body</span>
              <span className="text-[11px] text-slate-400 leading-relaxed">
                All transport headers, MIME multipart boundaries (<code className="text-cyan-400">--boundary</code>), and HTML markup have been automatically stripped by the static engine. The clean text below is what was evaluated by the ML classifier and SHAP explainer.
              </span>
            </div>
          </div>

          {/* Controls & Legend Bar */}
          <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
              <span className="text-slate-400 text-[11px] mr-1">Attribution Filters:</span>
              <button
                onClick={() => setShowPhishingHighlights(!showPhishingHighlights)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono border transition-all ${
                  showPhishingHighlights
                    ? 'bg-red-500/20 text-red-300 border-red-500/40 shadow-sm'
                    : 'bg-slate-900 text-slate-500 border-slate-800 line-through'
                }`}
              >
                <span className="w-2 h-2 rounded-full bg-red-400" />
                Phishing Triggers ({phishingTokens.length})
              </button>

              <button
                onClick={() => setShowLegitHighlights(!showLegitHighlights)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono border transition-all ${
                  showLegitHighlights
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-sm'
                    : 'bg-slate-900 text-slate-500 border-slate-800 line-through'
                }`}
              >
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                Benign Anchors ({legitTokens.length})
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => copyToClipboard(bodyText, setCopiedText)}
                className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono border border-slate-700 flex items-center gap-1.5 transition-colors"
                title="Copy clean parsed body text"
              >
                {copiedText ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3 text-slate-400" />
                    <span>Copy Clean Body</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Interactive Inspection Workspace */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 font-mono text-xs overflow-x-auto max-h-[460px] overflow-y-auto relative scrollbar-thin">
            {renderedContent}
          </div>

          {/* Forensic Micro-Footer */}
          <div className="flex items-center justify-between text-[11px] text-slate-400 px-1 font-mono">
            <span>Hover highlighted token for exact Shapley log-odds contribution values</span>
            <span>Parsed Body Size: {bodyText.length} characters</span>
          </div>
        </div>
      )}

      {/* TAB 1: HEADERS & AUTH */}
      {activeTab === 'headers' && (
        <div className="space-y-4">
          {/* Auth Protocol Matrix */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* SPF Card */}
            <div className="p-3.5 rounded-xl bg-slate-800/50 border border-slate-700/60 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-slate-400 block">SPF Protocol</span>
                <span className="text-sm font-bold font-mono text-slate-100 uppercase">
                  {headerFindings.spf_status || 'NONE'}
                </span>
              </div>
              {headerFindings.spf_status === 'pass' ? (
                <CheckCircle className="w-5 h-5 text-emerald-400" />
              ) : (
                <XCircle className="w-5 h-5 text-red-400" />
              )}
            </div>

            {/* DKIM Card */}
            <div className="p-3.5 rounded-xl bg-slate-800/50 border border-slate-700/60 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-slate-400 block">DKIM Signature</span>
                <span className="text-sm font-bold font-mono text-slate-100 uppercase">
                  {headerFindings.dkim_status || 'NONE'}
                </span>
              </div>
              {headerFindings.dkim_status === 'pass' ? (
                <CheckCircle className="w-5 h-5 text-emerald-400" />
              ) : (
                <XCircle className="w-5 h-5 text-red-400" />
              )}
            </div>

            {/* DMARC Card */}
            <div className="p-3.5 rounded-xl bg-slate-800/50 border border-slate-700/60 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-slate-400 block">DMARC Policy</span>
                <span className="text-sm font-bold font-mono text-slate-100 uppercase">
                  {headerFindings.dmarc_status || 'NONE'}
                </span>
              </div>
              {headerFindings.dmarc_status === 'pass' ? (
                <CheckCircle className="w-5 h-5 text-emerald-400" />
              ) : (
                <XCircle className="w-5 h-5 text-red-400" />
              )}
            </div>
          </div>

          {/* Spoofing & Domain Alignments */}
          <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/40 space-y-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Display-Name Impersonation Check:</span>
              <span className={`font-mono font-semibold px-2 py-0.5 rounded text-[11px] ${
                headerFindings.spoofing_detected 
                  ? 'bg-red-500/10 text-red-400 border border-red-500/20' 
                  : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              }`}>
                {headerFindings.spoofing_detected ? 'DECEPTIVE DISPLAY NAME' : 'NO DECEPTION'}
              </span>
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">From vs Reply-To Alignment:</span>
              <span className={`font-mono text-[11px] ${
                headerFindings.reply_to_mismatch ? 'text-amber-400 font-semibold' : 'text-slate-300'
              }`}>
                {headerFindings.reply_to_mismatch ? 'MISMATCH DETECTED' : 'ALIGNED'}
              </span>
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">From vs Return-Path Alignment:</span>
              <span className={`font-mono text-[11px] ${
                headerFindings.return_path_mismatch ? 'text-amber-400 font-semibold' : 'text-slate-300'
              }`}>
                {headerFindings.return_path_mismatch ? 'MISMATCH DETECTED' : 'ALIGNED'}
              </span>
            </div>
          </div>

          {/* Header Anomalies List */}
          {headerFindings.anomalies && headerFindings.anomalies.length > 0 && (
            <div className="p-3.5 rounded-xl bg-red-950/20 border border-red-900/30">
              <span className="text-xs font-semibold text-red-400 block mb-1.5">Detected Header Anomalies:</span>
              <ul className="space-y-1">
                {headerFindings.anomalies.map((ano, idx) => (
                  <li key={idx} className="text-xs text-red-300/90 flex items-start gap-1.5 font-mono">
                    <span className="text-red-400">•</span>
                    <span>{ano}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: STATIC URLS */}
      {activeTab === 'urls' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Static Heuristic URL Screening ({urlFindings.length} detected)</span>
            <span className="font-mono text-[10px] text-emerald-400">Zero Network Requests Made</span>
          </div>

          {urlFindings.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500 rounded-xl bg-slate-800/30 border border-slate-700/40">
              No embedded URLs found in message content.
            </div>
          ) : (
            <div className="space-y-2.5">
              {urlFindings.map((url, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs">
                  <div className="flex items-start justify-between gap-3 mb-1.5">
                    <div className="font-mono font-medium text-blue-300 break-all select-all">
                      {url.url}
                    </div>
                    <span className={`shrink-0 font-mono text-[11px] font-bold px-2 py-0.5 rounded ${
                      url.risk_score >= 50
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                        : url.risk_score >= 25
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}>
                      Score: {url.risk_score}/100
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-2 text-[10px] font-mono text-slate-400 mt-2">
                    <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-700/60">
                      Domain: {url.domain || 'N/A'}
                    </span>
                    <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-700/60">
                      Entropy: {Number(url.entropy || 0).toFixed(2)}
                    </span>
                    {url.is_ip && (
                      <span className="bg-red-950/80 text-red-300 px-2 py-0.5 rounded border border-red-700/60">
                        Raw IP Host
                      </span>
                    )}
                    {url.has_punycode && (
                      <span className="bg-red-950/80 text-red-300 px-2 py-0.5 rounded border border-red-700/60">
                        Punycode / IDN
                      </span>
                    )}
                    {url.suspicious_tld && (
                      <span className="bg-orange-950/80 text-orange-300 px-2 py-0.5 rounded border border-orange-700/60">
                        Suspicious TLD
                      </span>
                    )}
                    {url.brand_in_subdomain && (
                      <span className="bg-red-950/80 text-red-300 px-2 py-0.5 rounded border border-red-700/60">
                        Deceptive Subdomain
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: ATTACHMENTS */}
      {activeTab === 'attachments' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Passive Static Attachment Fingerprinting</span>
            <span className="font-mono text-[10px] text-emerald-400">Zero Attachment Execution</span>
          </div>

          {attachmentFindings.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500 rounded-xl bg-slate-800/30 border border-slate-700/40">
              No file attachments present in this email.
            </div>
          ) : (
            <div className="space-y-2.5">
              {attachmentFindings.map((att, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs">
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <Paperclip className="w-4 h-4 text-blue-400" />
                      <span className="font-mono font-semibold text-slate-200">{att.filename}</span>
                      <span className="text-[10px] font-mono text-slate-400">({att.size_bytes || 0} bytes)</span>
                    </div>
                    <span className={`font-mono text-[11px] font-bold px-2 py-0.5 rounded ${
                      att.risk_score >= 50
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}>
                      Risk: {att.risk_score}/100
                    </span>
                  </div>

                  <div className="p-2 rounded bg-slate-900/80 font-mono text-[10px] text-slate-400 break-all select-all flex items-center gap-1.5 mb-2">
                    <Hash className="w-3 h-3 text-cyan-400 shrink-0" />
                    <span>SHA-256: {att.sha256 || 'N/A'}</span>
                  </div>

                  {att.flags && att.flags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {att.flags.map((flag, fIdx) => (
                        <span key={fIdx} className="px-2 py-0.5 rounded text-[10px] font-mono bg-red-900/30 text-red-300 border border-red-700/40">
                          {flag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: SOCIAL ENGINEERING */}
      {activeTab === 'social' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Social Engineering & Linguistic Manipulation Cues</span>
            <span className="font-mono text-[11px] text-amber-400">
              Raw Score: {socialFindings.score || 0}/100
            </span>
          </div>

          {(socialFindings.categories_flagged || []).length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500 rounded-xl bg-slate-800/30 border border-slate-700/40">
              No significant social engineering markers detected.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {(socialFindings.categories_flagged || []).map((cat, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-amber-950/20 border border-amber-900/40">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-300 mb-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                    <span className="capitalize">{cat.replace(/_/g, ' ')}</span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Triggers psychological pressure targeting rapid, uncritical user compliance.
                  </p>
                </div>
              ))}
            </div>
          )}

          {socialFindings.detected_tokens && socialFindings.detected_tokens.length > 0 && (
            <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/40">
              <span className="text-[11px] font-semibold text-slate-400 block mb-1.5 font-mono">
                Matched Keyword Cues:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {socialFindings.detected_tokens.map((tok, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[11px]">
                    "{tok}"
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: RAW RFC-822 / MIME ENVELOPE SOURCE */}
      {activeTab === 'raw_source' && (
        <div className="space-y-4">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-start justify-between gap-3">
            <div className="flex items-start gap-2.5 text-xs text-slate-300">
              <Code className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-indigo-300 block">Raw RFC-822 / MIME Envelope Source</span>
                <span className="text-[11px] text-slate-400 leading-relaxed">
                  This is the exact byte stream transmitted over SMTP, including raw transport headers, cryptographic signatures (ARC/DKIM), and multipart boundary delimiters (<code className="text-indigo-300">--boundary</code>).
                </span>
              </div>
            </div>

            <button
              onClick={() => copyToClipboard(rawEmail, setCopiedRaw)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono border border-slate-700 flex items-center gap-1.5 transition-colors shrink-0"
              title="Copy complete raw RFC-822 email source"
            >
              {copiedRaw ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-slate-400" />
                  <span>Copy Source</span>
                </>
              )}
            </button>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800/80 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-[460px] overflow-y-auto select-text scrollbar-thin leading-relaxed">
            {rawEmail ? (
              <pre className="whitespace-pre-wrap">{rawEmail}</pre>
            ) : (
              <div className="text-center py-8 text-slate-500 italic">
                [Raw RFC-822 envelope not captured or email was analyzed via direct plain text body]
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
