import React, { useState } from 'react';
import Navbar from './components/Navbar';
import AnalyzeView from './pages/AnalyzeView';
import ResultView from './pages/ResultView';
import HistoryView from './pages/HistoryView';
import ModelPerformanceView from './pages/ModelPerformanceView';
import DocsView from './pages/DocsView';
import { Shield, HardDrive, Terminal } from 'lucide-react';

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
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      {/* Top Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
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

        {activeTab === 'docs' && (
          <DocsView />
        )}
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/80 bg-[#05080f] py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 font-mono text-[11px]">
            <Shield className="w-4 h-4 text-blue-500" />
            <span className="text-slate-300 font-semibold">PhishGuard SOC Platform</span>
            <span>—</span>
            <span>B.Sc. Final Year Capstone Project</span>
          </div>

          <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400">
            <span className="flex items-center gap-1">
              <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
              <span>Offline SQLite DB</span>
            </span>
            <span className="flex items-center gap-1">
              <Terminal className="w-3.5 h-3.5 text-emerald-400" />
              <span>Scikit-learn + SHAP CPU</span>
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
