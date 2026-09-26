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
  Lock,
  Terminal,
  Zap,
  RotateCcw,
  Copy,
  ScanLine,
  Mail,
  ChevronRight,
  History,
  ExternalLink,
  ShieldCheck,
  FileCheck
} from 'lucide-react';
import { api } from '../services/api';

export default function AnalyzeView({ onAnalysisComplete, onSelectInvestigation }) {
  const [rawEmail, setRawEmail] = useState('');
  const [fileName, setFileName] = useState('manual_input.eml');
  const [samples, setSamples] = useState([]);
  const [userTestedMails, setUserTestedMails] = useState([]);
  const [selectedSample, setSelectedSample] = useState(null);
  const [activePresetTab, setActivePresetTab] = useState('presets'); // 'presets' | 'user_tested'
  const [loading, setLoading] = useState(false);
  const [loadingHistoryItem, setLoadingHistoryItem] = useState(null);
  const [scanStep, setScanStep] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedFileMeta, setUploadedFileMeta] = useState(null);

  // Fetch synthetic presets and user's tested emails on mount
  useEffect(() => {
    let mounted = true;

    const loadData = async () => {
      try {
        const [sampleData, historyData] = await Promise.all([
          api.getSamples().catch(() => []),
          api.getHistory(1, 30).catch(() => []),
        ]);
        if (mounted) {
          if (Array.isArray(sampleData)) setSamples(sampleData);
          if (Array.isArray(historyData)) setUserTestedMails(historyData);
        }
      } catch (err) {
        console.warn('Could not prefetch samples or history:', err);
      }
    };

    loadData();
    return () => {
      mounted = false;
    };
  }, []);

  // Handle Synthetic Preset Selection
  const handleSelectSample = (sample) => {
    setSelectedSample(sample.filename);
    setRawEmail(sample.raw_content);
    setFileName(sample.filename);
    setUploadedFileMeta(null);
    setError(null);
  };

  // Inspect an email from the user's tested history
  const handleInspectUserMail = async (item) => {
    setLoadingHistoryItem(item.id);
    try {
      const detail = await api.getHistoryDetail(item.id);
      if (onSelectInvestigation) {
        onSelectInvestigation(detail);
      } else if (onAnalysisComplete) {
        onAnalysisComplete(detail);
      }
    } catch (err) {
      setError(`Failed to load investigation details: ${err.message}`);
    } finally {
      setLoadingHistoryItem(null);
    }
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
    setUploadedFileMeta({
      name: file.name,
      size: (file.size / 1024).toFixed(1) + ' KB',
      lastModified: new Date(file.lastModified).toLocaleTimeString()
    });

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

  // Execute Analysis with progressive HUD steps
  const handleAnalyze = async (e) => {
    e?.preventDefault();
    if (!rawEmail.trim()) {
      setError('Please select a demonstration sample, upload an .eml file, or paste raw email text.');
      return;
    }

    setLoading(true);
    setScanStep(1);
    setError(null);

    // Multi-step HUD progression
    const timer1 = setTimeout(() => setScanStep(2), 250);
    const timer2 = setTimeout(() => setScanStep(3), 500);
    const timer3 = setTimeout(() => setScanStep(4), 800);

    try {
      const result = await api.analyzeEmail(rawEmail, fileName);
      onAnalysisComplete(result);
    } catch (err) {
      setError(err.message || 'Analysis failed. Please check backend connection.');
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setLoading(false);
      setScanStep(0);
    }
  };

  const charCount = rawEmail.length;
  const lineCount = rawEmail ? rawEmail.split('\n').length : 0;

  // Helper function to format verdict badge for tested emails
  const getTestedMailBadge = (severity, score) => {
    if (severity === 'LOW' || score < 25) {
      return {
        label: 'LEGITIMATE (BENIGN)',
        className: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
      };
    }
    if (severity === 'MODERATE' || (score >= 25 && score < 50)) {
      return {
        label: 'SUSPICIOUS (SPAM)',
        className: 'bg-amber-500/15 text-amber-300 border-amber-500/30'
      };
    }
    return {
      label: 'PHISHING (SPAM / THREAT)',
      className: 'bg-red-500/15 text-red-300 border-red-500/30'
    };
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/40 via-slate-900/80 to-indigo-950/40 border border-slate-800/90 shadow-2xl backdrop-blur-xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
              <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-bold">
                Threat Triage Engine Active
              </span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white font-['Outfit']">
              Email Security Triage Workspace
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
              Multi-signal static inspection: SPF/DKIM authentication, regex URL heuristics, supervised Scikit-learn classification, mathematical SHAP attributions, and stylometric AI authorship detection.
            </p>
          </div>

          <div className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-emerald-400 text-xs font-mono shrink-0 shadow-inner">
            <Lock className="w-4 h-4 text-emerald-400" />
            <div>
              <div className="font-bold text-[11px] tracking-wide">ZERO OUTBOUND RISK</div>
              <div className="text-[10px] text-slate-400">0 URL visits | 0 attachment exec</div>
            </div>
          </div>
        </div>

        {/* Dual Preset Tabs: Synthetic Demos vs User's Tested Emails */}
        <div className="mt-6 pt-5 border-t border-slate-800/80 relative z-10">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-3.5">
            {/* Tab switch buttons */}
            <div className="flex items-center gap-2 bg-slate-950/80 p-1 rounded-xl border border-slate-800">
              <button
                type="button"
                onClick={() => setActivePresetTab('presets')}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium font-['Outfit'] transition-all ${
                  activePresetTab === 'presets'
                    ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                <span>Synthetic Presets ({samples.length})</span>
              </button>

              <button
                type="button"
                onClick={() => setActivePresetTab('user_tested')}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium font-['Outfit'] transition-all ${
                  activePresetTab === 'user_tested'
                    ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <History className="w-3.5 h-3.5 text-purple-400" />
                <span>Your Tested & Uploaded Emails ({userTestedMails.length})</span>
              </button>
            </div>

            <span className="text-[11px] font-mono text-slate-400 hidden sm:inline">
              {activePresetTab === 'presets' 
                ? 'Click any synthetic preset to auto-load in editor' 
                : 'Click any tested email to view its full forensic verdict'}
            </span>
          </div>

          {/* TAB 1: SYNTHETIC INCIDENT DEMONSTRATION PRESETS */}
          {activePresetTab === 'presets' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {samples.map((s) => {
                const isSelected = selectedSample === s.filename;
                const isPhish = s.label === 'Phishing';
                return (
                  <div
                    key={s.filename}
                    onClick={() => handleSelectSample(s)}
                    className={`p-3 rounded-xl cursor-pointer transition-all duration-200 border flex flex-col justify-between ${
                      isSelected
                        ? 'bg-blue-600/20 border-cyan-400 shadow-lg shadow-blue-500/20 transform scale-[1.02]'
                        : 'bg-slate-900/60 hover:bg-slate-800/80 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className={`text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded-full border ${
                        isPhish 
                          ? 'bg-red-500/10 text-red-400 border-red-500/30' 
                          : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      }`}>
                        {s.label}
                      </span>
                      {isSelected && (
                        <span className="text-[10px] font-mono text-cyan-400 flex items-center gap-1 font-semibold">
                          <Check className="w-3 h-3" /> Loaded
                        </span>
                      )}
                    </div>
                    <span className="text-xs font-medium text-slate-200 line-clamp-1 font-['Outfit']">
                      {s.subject || s.filename}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400 truncate mt-1">
                      {s.sender}
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          {/* TAB 2: USER'S TESTED & UPLOADED EMAILS */}
          {activePresetTab === 'user_tested' && (
            <div>
              {userTestedMails.length === 0 ? (
                <div className="p-8 text-center rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs text-slate-400 font-mono">
                  <FileCheck className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                  <p className="font-semibold text-slate-300 mb-1">No custom test emails analyzed yet.</p>
                  <p className="text-[11px] text-slate-500">
                    Upload an <span className="text-cyan-400">.eml</span> file or paste email text below and click <strong>"Execute Risk Analysis"</strong> to evaluate whether it's Legitimate or Phishing.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                  {userTestedMails.slice(0, 9).map((item) => {
                    const badge = getTestedMailBadge(item.severity, item.risk_score);
                    const isLoadingThis = loadingHistoryItem === item.id;
                    return (
                      <div
                        key={item.id}
                        onClick={() => handleInspectUserMail(item)}
                        className="p-3.5 rounded-xl cursor-pointer transition-all duration-200 border bg-slate-900/70 hover:bg-slate-800/90 border-slate-800 hover:border-slate-600 shadow-md flex flex-col justify-between group"
                      >
                        <div>
                          <div className="flex items-center justify-between gap-2 mb-2">
                            <span className={`text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded-full border ${badge.className}`}>
                              {badge.label}
                            </span>
                            <span className="text-[10px] font-mono text-slate-400 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
                              Score: {item.risk_score.toFixed(1)}
                            </span>
                          </div>

                          <h4 className="text-xs font-semibold text-slate-100 group-hover:text-blue-300 transition-colors line-clamp-1 font-['Outfit']">
                            {item.subject || 'Untitled Email'}
                          </h4>

                          <p className="text-[10px] font-mono text-slate-400 truncate mt-1">
                            {item.sender || 'Unknown Sender'}
                          </p>
                        </div>

                        <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/60 text-[10px] font-mono text-slate-500">
                          <span>{item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}</span>
                          <span className="text-blue-400 flex items-center gap-1 group-hover:underline">
                            {isLoadingThis ? <Loader2 className="w-3 h-3 animate-spin" /> : <ExternalLink className="w-3 h-3" />}
                            <span>Inspect Verdict</span>
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-center gap-2.5 shadow-lg">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Analysis Card */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-xl shadow-2xl space-y-5">
        {/* Cyber-Scanner File Dropzone */}
        <div
          onDragEnter={() => setDragActive(true)}
          onDragLeave={() => setDragActive(false)}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          className={`relative border-2 border-dashed rounded-2xl p-7 text-center transition-all duration-300 overflow-hidden ${
            dragActive
              ? 'border-cyan-400 bg-cyan-500/10 shadow-[0_0_30px_rgba(6,182,212,0.2)]'
              : 'border-slate-700/70 hover:border-blue-500/60 bg-slate-950/40'
          }`}
        >
          {/* Animated Laser Sweep Effect */}
          <div className="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent pointer-events-none animate-laser opacity-40"></div>

          <input
            type="file"
            id="email-file-input"
            accept=".eml,.txt,.msg"
            onChange={handleFileInput}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="flex flex-col items-center justify-center pointer-events-none relative z-10">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 text-cyan-400 flex items-center justify-center mb-3">
              <UploadCloud className="w-6 h-6 animate-pulse-subtle" />
            </div>
            <p className="text-xs font-semibold text-slate-200 font-['Outfit']">
              Drag & drop an <span className="font-mono text-cyan-400">.eml</span>, <span className="font-mono text-cyan-400">.msg</span>, or <span className="font-mono text-cyan-400">.txt</span> email file here, or click to browse
            </p>
            <p className="text-[11px] text-slate-400 mt-1 font-mono">
              RFC-822 MIME format, raw email headers, and multipart message bodies
            </p>
          </div>
        </div>

        {/* Uploaded File Confirmation Chip */}
        {uploadedFileMeta && (
          <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-800/40 flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2 text-cyan-300">
              <FileCheck className="w-4 h-4 text-cyan-400" />
              <span>Loaded File: <strong>{uploadedFileMeta.name}</strong> ({uploadedFileMeta.size})</span>
            </div>
            <button
              onClick={handleAnalyze}
              className="px-3 py-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold transition-colors"
            >
              Analyze This File Now
            </button>
          </div>
        )}

        {/* Format Guidance Banner */}
        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-start gap-2.5 text-xs text-slate-300">
          <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <span className="font-semibold text-slate-200">How Raw Email Ingestion Works: </span>
            <span className="text-slate-400 text-[11px]">
              You can paste either a plain email body OR the full raw message from Gmail / Outlook (via <em>"Show original"</em> / <em>"Download message"</em>). Raw emails naturally contain transport headers, MIME boundaries (<code className="text-cyan-400">--boundary</code>), and HTML code. PhishGuard automatically strips the code, validates authentication (SPF, DKIM, DMARC), and extracts clean text for AI evaluation.
            </span>
          </div>
        </div>

        {/* Raw Text Input Area with Code Toolbar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs pb-1">
            <label htmlFor="raw-email-input" className="font-semibold text-slate-300 flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>Raw RFC-822 / Text Message Content:</span>
            </label>
            <div className="flex items-center gap-3 font-mono text-[11px]">
              <span className="text-slate-400">
                File: <strong className="text-slate-200">{fileName}</strong>
              </span>
              <span className="text-slate-600">|</span>
              <span className="text-slate-400">{lineCount} lines / {charCount} chars</span>
              {rawEmail && (
                <button
                  type="button"
                  onClick={() => {
                    setRawEmail('');
                    setSelectedSample(null);
                    setUploadedFileMeta(null);
                    setFileName('manual_input.eml');
                  }}
                  className="text-slate-400 hover:text-red-400 transition-colors flex items-center gap-1"
                >
                  <RotateCcw className="w-3 h-3" />
                  <span>Clear</span>
                </button>
              )}
            </div>
          </div>

          <textarea
            id="raw-email-input"
            rows={11}
            value={rawEmail}
            onChange={(e) => setRawEmail(e.target.value)}
            placeholder="From: Security Team <security@paypa1-update.com>&#10;To: victim@example.com&#10;Subject: URGENT: Account Suspension in 24 Hours&#10;Date: Mon, 26 Sep 2026 12:00:00 +0000&#10;&#10;Dear Customer, Your account has been temporarily restricted due to suspicious login activity. Click below to verify your identity: http://192.168.1.100/verify-account"
            className="w-full p-4 rounded-xl bg-slate-950/90 border border-slate-800 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 text-xs font-mono text-slate-200 placeholder:text-slate-600 transition-all leading-relaxed shadow-inner"
          />
        </div>

        {/* Action Button & Live Pipeline HUD */}
        <div className="pt-2">
          {loading ? (
            /* Progressive Triage HUD */
            <div className="p-4 rounded-xl bg-slate-950/80 border border-cyan-500/40 space-y-3 shadow-lg">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-cyan-400 font-bold flex items-center gap-2">
                  <ScanLine className="w-4 h-4 animate-spin text-cyan-400" />
                  <span>EXECUTING FORENSIC TRIAGE PIPELINE...</span>
                </span>
                <span className="text-slate-400">Step {scanStep}/4</span>
              </div>

              {/* Step checklist */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono">
                <div className={`flex items-center gap-2 ${scanStep >= 1 ? 'text-cyan-300' : 'text-slate-600'}`}>
                  {scanStep > 1 ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <ChevronRight className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />}
                  <span>1. Parsing RFC-822 MIME & Headers</span>
                </div>
                <div className={`flex items-center gap-2 ${scanStep >= 2 ? 'text-cyan-300' : 'text-slate-600'}`}>
                  {scanStep > 2 ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <ChevronRight className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />}
                  <span>2. Scanning Static URLs & Entropy</span>
                </div>
                <div className={`flex items-center gap-2 ${scanStep >= 3 ? 'text-cyan-300' : 'text-slate-600'}`}>
                  {scanStep > 3 ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <ChevronRight className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />}
                  <span>3. ML Inference & SHAP Attribution</span>
                </div>
                <div className={`flex items-center gap-2 ${scanStep >= 4 ? 'text-cyan-300' : 'text-slate-600'}`}>
                  {scanStep >= 4 ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <ChevronRight className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />}
                  <span>4. Module A Stylometry & Risk Synthesis</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Info className="w-4 h-4 text-cyan-400 shrink-0" />
                <span>Deterministic static scoring: zero telemetry, 100% offline.</span>
              </div>

              <button
                type="button"
                disabled={!rawEmail.trim()}
                onClick={handleAnalyze}
                className={`w-full sm:w-auto px-7 py-3 rounded-xl font-bold text-xs tracking-wider font-['Outfit'] uppercase flex items-center justify-center gap-2.5 transition-all shadow-xl ${
                  !rawEmail.trim()
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50'
                    : 'bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white shadow-blue-600/30 hover:scale-[1.02]'
                }`}
              >
                <ShieldAlert className="w-4 h-4 text-white" />
                <span>Execute Risk Analysis</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
