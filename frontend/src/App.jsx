import React, { useState, Component } from 'react';
import Navbar from './components/Navbar';
import AnalyzeView from './pages/AnalyzeView';
import ResultView from './pages/ResultView';
import HistoryView from './pages/HistoryView';
import ModelPerformanceView from './pages/ModelPerformanceView';
import { Shield, HardDrive, Terminal, AlertTriangle, RefreshCw, Lock } from 'lucide-react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-2xl mx-auto my-12 p-8 rounded-2xl bg-red-950/40 border border-red-800/60 text-center space-y-4 shadow-2xl backdrop-blur-xl">
          <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 mx-auto flex items-center justify-center">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-white font-['Outfit']">Component Error Detected</h2>
          <p className="text-xs text-red-300 font-mono bg-red-950/70 p-3 rounded-lg border border-red-900/50 text-left overflow-x-auto">
            {this.state.error?.message || String(this.state.error)}
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.reload();
            }}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold inline-flex items-center gap-2 border border-slate-700 transition-colors shadow-md"
          >
            <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
            <span>Reload Application</span>
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const [activeTab, setActiveTab] = useState('analyze');
  const [currentResult, setCurrentResult] = useState(null);

  const handleAnalysisComplete = (result) => {
    setCurrentResult(result);
    setActiveTab('result');
  };

  const handleSelectInvestigation = (detail) => {
    setCurrentResult(detail);
    setActiveTab('result');
  };

  const handleReset = () => {
    setCurrentResult(null);
    setActiveTab('analyze');
  };

  return (
    <div className="min-h-screen bg-[#050811] text-slate-100 flex flex-col relative selection:bg-blue-600 selection:text-white overflow-hidden">
      {/* Background Cyber Glow Effects */}
      <div className="pointer-events-none absolute top-0 left-1/4 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl -z-10 animate-pulse-subtle"></div>
      <div className="pointer-events-none absolute top-40 right-1/4 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl -z-10"></div>
      <div className="pointer-events-none absolute bottom-10 left-1/3 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl -z-10"></div>

      {/* Top Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary>
          {activeTab === 'analyze' && (
            <AnalyzeView onAnalysisComplete={handleAnalysisComplete} />
          )}

          {activeTab === 'result' && (
            <ResultView analysisResult={currentResult} onReset={handleReset} />
          )}

          {activeTab === 'history' && (
            <HistoryView onSelectInvestigation={handleSelectInvestigation} />
          )}

          {activeTab === 'performance' && (
            <ModelPerformanceView />
          )}
        </ErrorBoundary>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/80 bg-[#04060c] py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5 font-mono text-[11px]">
            <Shield className="w-4 h-4 text-cyan-400" />
            <span className="text-slate-300 font-semibold font-['Outfit']">PhishGuard SOC Platform</span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">Explainable Triage & Threat Intelligence</span>
          </div>

          <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400">
            <span className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              <span>Zero-Outbound Invariant</span>
            </span>
            <span className="flex items-center gap-1.5">
              <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
              <span>Local SQLite</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5 text-indigo-400" />
              <span>Scikit-learn + SHAP CPU</span>
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
