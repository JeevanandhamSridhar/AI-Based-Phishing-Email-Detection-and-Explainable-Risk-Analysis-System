import React, { useState } from 'react';
import { 
  ArrowLeft, 
  Download, 
  Copy, 
  Check, 
  Calendar, 
  User, 
  Globe, 
  Hash, 
  ShieldAlert, 
  FileDown,
  Printer,
  FileCode,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import RiskMeter from '../components/RiskMeter';
import FactorBreakdown from '../components/FactorBreakdown';
import XaiExplainer from '../components/XaiExplainer';
import AuthorshipCard from '../components/AuthorshipCard';
import ForensicInspector from '../components/ForensicInspector';
import { api } from '../services/api';

export default function ResultView({ analysisResult, onReset }) {
  const [copiedHash, setCopiedHash] = useState(false);
  const [activeForensicTab, setActiveForensicTab] = useState('xai_body');

  if (!analysisResult) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center glass-panel rounded-2xl border border-slate-800">
        <p className="text-slate-400 text-sm mb-4">No active incident analysis loaded.</p>
        <button
          onClick={onReset}
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold font-['Outfit'] transition-all shadow-lg shadow-blue-600/30"
        >
          Initialize Email Triage
        </button>
      </div>
    );
  }

  const {
    id,
    timestamp,
    email_metadata = {},
    overall_risk = {},
    factor_breakdown = {},
    explainability = {},
    ai_authorship = {},
    url_findings = [],
    header_findings = {},
    attachment_findings = [],
    social_findings = {},
  } = analysisResult;

  const copySha256 = () => {
    if (email_metadata.sha256) {
      navigator.clipboard.writeText(email_metadata.sha256);
      setCopiedHash(true);
      setTimeout(() => setCopiedHash(false), 2000);
    }
  };

  const handleDownloadPdf = () => {
    const url = api.getPdfDownloadUrl(id);
    window.open(url, '_blank');
  };

  const handleExportJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(analysisResult, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `forensic-report-${id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Top Action & Navigation Header */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800/90 shadow-2xl relative overflow-hidden">
        {/* Decorative Top Accent Glow */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-cyan-400 to-indigo-500" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <button
                onClick={onReset}
                className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors group"
              >
                <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" />
                <span>Return to Workspace</span>
              </button>
              <span className="text-slate-700">|</span>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/40">
                Incident ID: {id ? id.substring(0, 18) : 'N/A'}
              </span>
            </div>

            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white font-['Outfit'] break-words">
              {email_metadata.subject || 'Investigation Report'}
            </h1>
          </div>

          {/* Action Toolbar */}
          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <button
              onClick={handleDownloadPdf}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 flex items-center gap-2 font-['Outfit'] transition-all"
            >
              <FileDown className="w-4 h-4" />
              <span>Download PDF</span>
            </button>

            <button
              onClick={handleExportJson}
              className="px-3 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-mono border border-slate-700/80 flex items-center gap-1.5 transition-colors"
              title="Export Full Incident Telemetry JSON"
            >
              <FileCode className="w-3.5 h-3.5 text-cyan-400" />
              <span>JSON</span>
            </button>

            <button
              onClick={handlePrint}
              className="px-3 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-mono border border-slate-700/80 flex items-center gap-1.5 transition-colors"
              title="Print Briefing Sheet"
            >
              <Printer className="w-3.5 h-3.5 text-slate-400" />
            </button>

            <button
              onClick={onReset}
              className="px-3.5 py-2 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 flex items-center gap-1.5 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span>New Triage</span>
            </button>
          </div>
        </div>

        {/* Email Metadata Ribbon */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-4 text-xs font-mono">
          <div className="flex items-center gap-2.5 text-slate-300 p-2 rounded-xl bg-slate-950/40 border border-slate-800/50">
            <User className="w-4 h-4 text-blue-400 shrink-0" />
            <div className="truncate">
              <span className="text-[10px] text-slate-500 block uppercase">Sender</span>
              <span className="truncate text-slate-200" title={email_metadata.from_header}>{email_metadata.from_header || 'Unknown'}</span>
            </div>
          </div>

          <div className="flex items-center gap-2.5 text-slate-300 p-2 rounded-xl bg-slate-950/40 border border-slate-800/50">
            <Globe className="w-4 h-4 text-indigo-400 shrink-0" />
            <div className="truncate">
              <span className="text-[10px] text-slate-500 block uppercase">Sender Domain</span>
              <span className="truncate font-semibold text-slate-200">{email_metadata.sender_domain || 'N/A'}</span>
            </div>
          </div>

          <div className="flex items-center gap-2.5 text-slate-300 p-2 rounded-xl bg-slate-950/40 border border-slate-800/50">
            <Calendar className="w-4 h-4 text-purple-400 shrink-0" />
            <div className="truncate">
              <span className="text-[10px] text-slate-500 block uppercase">Triage Timestamp</span>
              <span className="truncate text-slate-300">{timestamp ? new Date(timestamp).toLocaleString() : 'N/A'}</span>
            </div>
          </div>

          <div className="flex items-center justify-between p-2 rounded-xl bg-slate-950/70 border border-slate-800 text-slate-400">
            <div className="truncate flex items-center gap-2">
              <Hash className="w-4 h-4 text-cyan-400 shrink-0" />
              <div className="truncate">
                <span className="text-[10px] text-slate-500 block uppercase">SHA-256 Fingerprint</span>
                <span className="truncate text-[11px] font-mono text-cyan-300">
                  {email_metadata.sha256 ? `${email_metadata.sha256.substring(0, 16)}...` : 'N/A'}
                </span>
              </div>
            </div>
            <button
              onClick={copySha256}
              title="Copy SHA-256 fingerprint"
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
            >
              {copiedHash ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Main Forensic Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Risk Gauge & Factor Breakdown (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <RiskMeter
            score={overall_risk.score}
            severity={overall_risk.severity}
            bracket={overall_risk.threshold_bracket}
          />

          <FactorBreakdown factorBreakdown={factor_breakdown} />

          <AuthorshipCard aiAuthorship={ai_authorship} />
        </div>

        {/* Right Column: Explainability & Forensic Inspector (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <XaiExplainer 
            explainability={explainability} 
            onViewInBody={() => setActiveForensicTab('xai_body')}
          />

          <ForensicInspector
            activeTab={activeForensicTab}
            onTabChange={setActiveForensicTab}
            headerFindings={header_findings}
            urlFindings={url_findings}
            attachmentFindings={attachment_findings}
            socialFindings={social_findings}
            emailMetadata={email_metadata}
            explainability={explainability}
          />
        </div>
      </div>
    </div>
  );
}
