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
  FileDown 
} from 'lucide-react';
import RiskMeter from '../components/RiskMeter';
import FactorBreakdown from '../components/FactorBreakdown';
import XaiExplainer from '../components/XaiExplainer';
import AuthorshipCard from '../components/AuthorshipCard';
import ForensicInspector from '../components/ForensicInspector';
import { api } from '../services/api';

export default function ResultView({ analysisResult, onReset }) {
  const [copiedHash, setCopiedHash] = useState(false);

  if (!analysisResult) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center">
        <p className="text-slate-400 text-sm mb-4">No analysis report selected.</p>
        <button
          onClick={onReset}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold"
        >
          Analyze an Email
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

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Top Action & Navigation Header */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <button
                onClick={onReset}
                className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Workspace</span>
              </button>
              <span className="text-slate-600">|</span>
              <span className="text-xs font-mono text-cyan-400">Incident ID: {id}</span>
            </div>

            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white font-['Outfit'] break-words">
              {email_metadata.subject || 'Investigation Report'}
            </h1>
          </div>

          {/* Action Toolbar */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleDownloadPdf}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-blue-600/30 flex items-center gap-2 font-['Outfit'] transition-all"
            >
              <FileDown className="w-4 h-4" />
              <span>Download Forensic PDF</span>
            </button>

            <button
              onClick={onReset}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
            >
              New Triage
            </button>
          </div>
        </div>

        {/* Email Metadata Ribbon */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-4 text-xs font-mono">
          <div className="flex items-center gap-2 text-slate-300">
            <User className="w-4 h-4 text-blue-400 shrink-0" />
            <div className="truncate">
              <span className="text-[10px] text-slate-500 block uppercase">Sender</span>
              <span className="truncate">{email_metadata.from_header || 'Unknown'}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-slate-300">
            <Globe className="w-4 h-4 text-indigo-400 shrink-0" />
            <div className="truncate">
              <span className="text-[10px] text-slate-500 block uppercase">Sender Domain</span>
              <span className="truncate font-semibold text-slate-200">{email_metadata.sender_domain || 'N/A'}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-slate-300">
            <Calendar className="w-4 h-4 text-purple-400 shrink-0" />
            <div>
              <span className="text-[10px] text-slate-500 block uppercase">Triage Timestamp</span>
              <span>{timestamp ? new Date(timestamp).toLocaleString() : 'N/A'}</span>
            </div>
          </div>

          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-slate-400">
            <div className="truncate flex items-center gap-1.5">
              <Hash className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span className="truncate text-[10px]">
                {email_metadata.sha256 ? `${email_metadata.sha256.substring(0, 16)}...` : 'N/A'}
              </span>
            </div>
            <button
              onClick={copySha256}
              title="Copy SHA-256 fingerprint"
              className="text-slate-400 hover:text-white transition-colors"
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
          <XaiExplainer explainability={explainability} />

          <ForensicInspector
            headerFindings={header_findings}
            urlFindings={url_findings}
            attachmentFindings={attachment_findings}
            socialFindings={social_findings}
            emailMetadata={email_metadata}
          />
        </div>
      </div>
    </div>
  );
}
