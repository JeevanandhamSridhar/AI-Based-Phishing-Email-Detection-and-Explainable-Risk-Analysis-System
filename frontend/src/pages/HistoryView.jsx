import React, { useState, useEffect, useMemo } from 'react';
import { 
  History, 
  Search, 
  Filter, 
  ExternalLink, 
  FileDown, 
  Loader2, 
  AlertOctagon, 
  AlertTriangle, 
  Info, 
  CheckCircle2, 
  RefreshCw,
  Shield,
  Layers,
  Sparkles,
  X,
  FileText
} from 'lucide-react';
import { api } from '../services/api';

export default function HistoryView({ onSelectInvestigation }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [error, setError] = useState(null);
  const [previewItem, setPreviewItem] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getHistory(page, 50, selectedSeverity);
      setHistoryItems(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load investigation history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, selectedSeverity]);

  // Filter items locally by search query
  const filteredItems = useMemo(() => {
    return historyItems.filter((item) => {
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        (item.subject && item.subject.toLowerCase().includes(q)) ||
        (item.sender && item.sender.toLowerCase().includes(q)) ||
        (item.sender_domain && item.sender_domain.toLowerCase().includes(q)) ||
        (item.id && item.id.toLowerCase().includes(q))
      );
    });
  }, [historyItems, searchQuery]);

  // Statistics calculation for the quick stats banner
  const stats = useMemo(() => {
    const total = historyItems.length;
    if (total === 0) return { total: 0, critical: 0, avgScore: 0 };
    const critical = historyItems.filter(i => i.severity === 'CRITICAL').length;
    const avgScore = (historyItems.reduce((acc, i) => acc + (i.risk_score || 0), 0) / total).toFixed(1);
    return { total, critical, avgScore };
  }, [historyItems]);

  const handleInspect = async (id) => {
    try {
      const detail = await api.getHistoryDetail(id);
      onSelectInvestigation(detail);
    } catch (err) {
      alert(`Could not load investigation: ${err.message}`);
    }
  };

  const getSeverityBadge = (severity, score) => {
    const sc = typeof score === 'number' ? score.toFixed(1) : score;
    switch (severity) {
      case 'CRITICAL':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-mono text-[11px] font-bold bg-red-500/15 text-red-300 border border-red-500/30 shadow-sm shadow-red-500/10">
            <AlertOctagon className="w-3.5 h-3.5 text-red-400" />
            <span>CRITICAL {sc}</span>
          </span>
        );
      case 'HIGH':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-mono text-[11px] font-bold bg-orange-500/15 text-orange-300 border border-orange-500/30">
            <AlertTriangle className="w-3.5 h-3.5 text-orange-400" />
            <span>HIGH {sc}</span>
          </span>
        );
      case 'MODERATE':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-mono text-[11px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
            <Info className="w-3.5 h-3.5 text-amber-400" />
            <span>MODERATE {sc}</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-mono text-[11px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>BENIGN {sc}</span>
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header Bar */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800/90 shadow-2xl relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500" />
        
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <History className="w-5 h-5 text-blue-400" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white font-['Outfit']">
              Investigation Ledger
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            Cryptographically fingerprinted audit record of all email security assessments and triage outcomes.
          </p>
        </div>

        {/* Quick SOC stats chip */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-3 bg-slate-950/60 p-2 px-3 rounded-xl border border-slate-800 font-mono text-xs">
            <div>
              <span className="text-[10px] text-slate-500 block">TOTAL LOGS</span>
              <span className="font-bold text-slate-200">{stats.total}</span>
            </div>
            <div className="w-px h-6 bg-slate-800" />
            <div>
              <span className="text-[10px] text-slate-500 block">CRITICAL</span>
              <span className="font-bold text-red-400">{stats.critical}</span>
            </div>
            <div className="w-px h-6 bg-slate-800" />
            <div>
              <span className="text-[10px] text-slate-500 block">AVG RISK</span>
              <span className="font-bold text-cyan-400">{stats.avgScore}</span>
            </div>
          </div>

          <button
            onClick={fetchHistory}
            disabled={loading}
            className="px-3.5 py-2.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs font-mono border border-slate-700 flex items-center gap-2 transition-colors shrink-0 shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-400' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-md flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 transform -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by subject, sender, or incident ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-200 placeholder:text-slate-600 focus:border-blue-500 focus:outline-none font-mono"
          />
        </div>

        {/* Severity Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-500 shrink-0 mr-1" />
          {['ALL', 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'].map((tier) => (
            <button
              key={tier}
              onClick={() => setSelectedSeverity(tier)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
                selectedSeverity === tier
                  ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/30'
                  : 'bg-slate-800/70 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* Records Table */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800/90 shadow-2xl overflow-hidden">
        {loading ? (
          <div className="py-20 text-center flex flex-col items-center justify-center gap-3">
            <Loader2 className="w-7 h-7 animate-spin text-blue-400" />
            <span className="text-xs text-slate-400 font-mono">Querying forensic ledger records...</span>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="py-20 text-center text-xs text-slate-500 font-mono">
            No investigation records found matching criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px] uppercase tracking-wider">
                  <th className="pb-3.5 pr-4">Timestamp</th>
                  <th className="pb-3.5 pr-4">Subject & ID</th>
                  <th className="pb-3.5 pr-4">Sender & Domain</th>
                  <th className="pb-3.5 pr-4">Composite Risk</th>
                  <th className="pb-3.5 pr-4">AI Likelihood</th>
                  <th className="pb-3.5 text-right">Forensic Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition-colors group">
                    <td className="py-4 pr-4 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                      {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-4 pr-4 font-medium text-slate-200 max-w-xs truncate">
                      <span className="font-semibold text-slate-100 group-hover:text-blue-300 transition-colors" title={item.subject}>
                        {item.subject || 'Untitled'}
                      </span>
                      <span className="block font-mono text-[10px] text-slate-500 truncate mt-0.5">
                        {item.id}
                      </span>
                    </td>
                    <td className="py-4 pr-4 text-slate-300 max-w-[200px] truncate">
                      <span className="text-slate-200 block truncate" title={item.sender}>{item.sender}</span>
                      <span className="block font-mono text-[10px] text-slate-400">
                        {item.sender_domain || 'N/A'}
                      </span>
                    </td>
                    <td className="py-4 pr-4 whitespace-nowrap">
                      {getSeverityBadge(item.severity, item.risk_score)}
                    </td>
                    <td className="py-4 pr-4 whitespace-nowrap font-mono text-xs">
                      <span className="px-2 py-0.5 rounded bg-purple-950/40 border border-purple-800/40 text-purple-300">
                        {Number(item.ai_generated_likelihood) <= 1.0 
                          ? Math.round(Number(item.ai_generated_likelihood || 0) * 100) 
                          : Math.round(Number(item.ai_generated_likelihood || 0))}% AI
                      </span>
                    </td>
                    <td className="py-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleInspect(item.id)}
                          className="px-3 py-1.5 rounded-lg bg-blue-600/15 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 text-xs font-medium font-['Outfit'] transition-all inline-flex items-center gap-1.5 shadow-sm"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          <span>Inspect</span>
                        </button>
                        <a
                          href={api.getPdfDownloadUrl(item.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-mono transition-colors inline-flex items-center gap-1.5"
                          title="Download Evidence PDF"
                        >
                          <FileDown className="w-3.5 h-3.5" />
                          <span>PDF</span>
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
