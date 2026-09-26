import React, { useState } from 'react';
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
  Lock 
} from 'lucide-react';

export default function ForensicInspector({
  headerFindings = {},
  urlFindings = [],
  attachmentFindings = [],
  socialFindings = {},
  emailMetadata = {},
}) {
  const [activeTab, setActiveTab] = useState('headers');

  const tabs = [
    { id: 'headers', label: 'Headers & Auth', count: headerFindings.spoofing_detected ? 'Alert' : null },
    { id: 'urls', label: 'Static URLs', count: urlFindings.length },
    { id: 'attachments', label: 'Attachments', count: attachmentFindings.length },
    { id: 'social', label: 'Social Engineering', count: (socialFindings.categories_flagged || []).length },
  ];

  return (
    <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl">
      {/* Tab Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-5 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <span>{tab.label}</span>
                {tab.count !== null && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : 'bg-slate-800 text-slate-400 border border-slate-700/60'
                    }`}
                  >
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
        <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 hidden sm:inline-block">
          Passive Forensic Mode
        </span>
      </div>

      {/* Tab Content 1: Headers & Authentication */}
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

      {/* Tab Content 2: Static URLs */}
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

      {/* Tab Content 3: Attachments */}
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

      {/* Tab Content 4: Social Engineering */}
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
    </div>
  );
}
