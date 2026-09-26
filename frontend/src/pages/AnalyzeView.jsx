import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, 
  FileText, 
  Send, 
  Sparkles, 
  ShieldAlert, 
  AlertCircle, 
  Loader2, 
  Check, 
  Info, 
  Lock 
} from 'lucide-react';
import { api } from '../services/api';

export default function AnalyzeView({ onAnalysisComplete }) {
  const [rawEmail, setRawEmail] = useState('');
  const [fileName, setFileName] = useState('sample_email.eml');
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);

  // Fetch synthetic presets on mount
  useEffect(() => {
    let mounted = true;
    const loadSamples = async () => {
      try {
        const data = await api.getSamples();
        if (mounted && Array.isArray(data)) {
          setSamples(data);
        }
      } catch (err) {
        console.warn('Could not prefetch sample emails:', err);
      }
    };
    loadSamples();
    return () => {
      mounted = false;
    };
  }, []);

  // Handle Preset Selection
  const handleSelectSample = (sample) => {
    setSelectedSample(sample.filename);
    setRawEmail(sample.raw_content);
    setFileName(sample.filename);
    setError(null);
  };

  // Handle file drop & selection
  const handleFileDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      processSelectedFile(e.target.files[0]);
    }
  };

  const processSelectedFile = (file) => {
    setFileName(file.name);
    setSelectedSample(null);
    const reader = new FileReader();
    reader.onload = (event) => {
      setRawEmail(event.target.result);
      setError(null);
    };
    reader.onerror = () => {
      setError('Failed to read file. Please ensure it is a valid text or .eml file.');
    };
    reader.readAsText(file);
  };

  // Execute Analysis
  const handleAnalyze = async (e) => {
    e?.preventDefault();
    if (!rawEmail.trim()) {
      setError('Please select a demonstration sample, upload an .eml file, or paste raw email text.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await api.analyzeEmail(rawEmail, fileName);
      onAnalysisComplete(result);
    } catch (err) {
      setError(err.message || 'Analysis failed. Please check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/40 via-slate-900/60 to-indigo-950/40 border border-slate-800 shadow-xl backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white font-['Outfit']">
              Email Security Triage Workspace
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
              Inspect suspicious emails against multi-factor static heuristics, supervised ML classification, SHAP feature attributions, and stylometric AI authorship signals.
            </p>
          </div>

          <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-900/80 border border-slate-700/60 text-emerald-400 text-xs font-mono shrink-0">
            <Lock className="w-4 h-4 text-emerald-400" />
            <div>
              <div className="font-semibold">DEFENSIVE INVARIANTS</div>
              <div className="text-[10px] text-slate-400">0 URL visits | 0 exec</div>
            </div>
          </div>
        </div>

        {/* Synthetic Demonstration Preset Badges */}
        {samples.length > 0 && (
          <div className="mt-5 pt-4 border-t border-slate-800/80">
            <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-300">
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              <span>One-Click Synthetic Demonstration Presets:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {samples.map((s) => {
                const isSelected = selectedSample === s.filename;
                const isPhish = s.label === 'Phishing';
                return (
                  <button
                    key={s.filename}
                    onClick={() => handleSelectSample(s)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all flex items-center gap-2 border ${
                      isSelected
                        ? 'bg-blue-600 border-blue-400 text-white font-semibold shadow-md shadow-blue-600/30'
                        : 'bg-slate-850/80 hover:bg-slate-800 border-slate-700/70 text-slate-300'
                    }`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${isPhish ? 'bg-red-400' : 'bg-emerald-400'}`} />
                    <span className="truncate max-w-[200px]">{s.subject || s.filename}</span>
                    <span className={`text-[9px] uppercase px-1 py-0.2 rounded ${isPhish ? 'bg-red-950 text-red-300' : 'bg-emerald-950 text-emerald-300'}`}>
                      {s.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Analysis Card */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl space-y-5">
        {/* Drag and Drop Zone */}
        <div
          onDragEnter={() => setDragActive(true)}
          onDragLeave={() => setDragActive(false)}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-all ${
            dragActive
              ? 'border-blue-500 bg-blue-500/10'
              : 'border-slate-700/70 hover:border-slate-600 bg-slate-850/40'
          }`}
        >
          <input
            type="file"
            id="email-file-input"
            accept=".eml,.txt"
            onChange={handleFileInput}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="flex flex-col items-center justify-center pointer-events-none">
            <UploadCloud className="w-8 h-8 text-blue-400 mb-2" />
            <p className="text-xs font-medium text-slate-200">
              Drag & drop an <span className="font-mono text-blue-400">.eml</span> or <span className="font-mono text-blue-400">.txt</span> email file here, or click to browse
            </p>
            <p className="text-[11px] text-slate-400 mt-1">
              Supports RFC-822 MIME format, raw email headers, and multipart message content
            </p>
          </div>
        </div>

        {/* Raw Text Input Area */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <label htmlFor="raw-email-input" className="font-semibold text-slate-300 flex items-center gap-2">
              <FileText className="w-3.5 h-3.5 text-blue-400" />
              <span>Raw RFC-822 Message Content:</span>
            </label>
            <div className="flex items-center gap-3">
              <span className="font-mono text-[11px] text-slate-400">
                File: <strong className="text-slate-200">{fileName}</strong>
              </span>
              {rawEmail && (
                <button
                  type="button"
                  onClick={() => {
                    setRawEmail('');
                    setSelectedSample(null);
                    setFileName('manual_input.eml');
                  }}
                  className="text-slate-400 hover:text-slate-200 text-[11px] underline"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          <textarea
            id="raw-email-input"
            rows={12}
            value={rawEmail}
            onChange={(e) => setRawEmail(e.target.value)}
            placeholder="From: Security Team <security@paypa1-update.com>&#10;To: victim@example.com&#10;Subject: URGENT: Account Suspension in 24 Hours&#10;Date: Mon, 26 Sep 2026 12:00:00 +0000&#10;&#10;Dear Customer, Your account has been temporarily restricted due to suspicious login activity. Click below to verify your identity: http://192.168.1.100/verify-account"
            className="w-full p-4 rounded-xl bg-slate-950/80 border border-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-xs font-mono text-slate-200 placeholder:text-slate-600 transition-colors leading-relaxed"
          />
        </div>

        {/* Action Button & Status Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Info className="w-4 h-4 text-blue-400 shrink-0" />
            <span>Analysis executes locally: zero external data transmission.</span>
          </div>

          <button
            type="button"
            disabled={loading || !rawEmail.trim()}
            onClick={handleAnalyze}
            className={`w-full sm:w-auto px-6 py-3 rounded-xl font-semibold text-xs tracking-wide font-['Outfit'] uppercase flex items-center justify-center gap-2.5 transition-all shadow-lg ${
              loading || !rawEmail.trim()
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50'
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-blue-600/30'
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Running Forensic Triage Pipeline...</span>
              </>
            ) : (
              <>
                <ShieldAlert className="w-4 h-4 text-white" />
                <span>Execute Risk Analysis</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
