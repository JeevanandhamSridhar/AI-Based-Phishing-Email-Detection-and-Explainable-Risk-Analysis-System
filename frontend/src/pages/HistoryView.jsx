import React, { useState, useEffect } from 'react';
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
  RefreshCw 
} from 'lucide-react';
import { api } from '../services/api';

export default function HistoryView({ onSelectInvestigation }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [error, setError] = useState(null);

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
  const filteredItems = historyItems.filter((item) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      (item.subject && item.subject.toLowerCase().includes(q)) ||
      (item.sender && item.sender.toLowerCase().includes(q)) ||
      (item.sender_domain && item.sender_domain.toLowerCase().includes(q)) ||
      (item.id && item.id.toLowerCase().includes(q))
    );
  });

  const handleInspect = async (id) => {
    try {
      const detail = await api.getHistoryDetail(id);
      onSelectInvestigation(detail);
    } catch (err) {
      alert(`Could not load investigation: ${err.message}`);
    }
  };

  const getSeverityBadge = (severity, score) => {
    switch (severity) {
      case 'CRITICAL':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-mono text-[11px] font-bold bg-red-500/10 text-red-400 border border-red-500/20">
            <AlertOctagon className="w-3 h-3 text-red-400" />
            <span>{score.toFixed(1)}</span>
          </span>
        );
      case 'HIGH':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-mono text-[11px] font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20">
            <AlertTriangle className="w-3 h-3 text-orange-400" />
            <span>{score.toFixed(1)}</span>
          </span>
        );
      case 'MODERATE':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-mono text-[11px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Info className="w-3 h-3 text-amber-400" />
            <span>{score.toFixed(1)}</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-mono text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>{score.toFixed(1)}</span>
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header Bar */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <History className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold tracking-tight text-white font-['Outfit']">
              Investigation Ledger
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            Immutable audit record of all email security assessments and triage outcomes.
          </p>
        </div>

        <button
          onClick={fetchHistory}
          disabled={loading}
          className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 flex items-center gap-2 transition-colors self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          <span>Refresh Ledger</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 transform -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by subject, sender, or incident ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs text-slate-200 placeholder:text-slate-600 focus:border-blue-500 focus:outline-none"
          />
        </div>

        {/* Severity Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-500 shrink-0 mr-1" />
          {['ALL', 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'].map((tier) => (
            <button
              key={tier}
              onClick={() => setSelectedSeverity(tier)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-mono transition-colors ${
                selectedSeverity === tier
                  ? 'bg-blue-600 text-white font-semibold'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* Records Table */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl overflow-hidden">
        {loading ? (
          <div className="py-16 text-center flex flex-col items-center justify-center gap-3">
            <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
            <span className="text-xs text-slate-400 font-mono">Querying SQLite investigation records...</span>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="py-16 text-center text-xs text-slate-500">
            No investigation records found matching criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono text-[11px] uppercase">
                  <th className="pb-3 pr-4">Timestamp</th>
                  <th className="pb-3 pr-4">Subject</th>
                  <th className="pb-3 pr-4">Sender</th>
                  <th className="pb-3 pr-4">Composite Score</th>
                  <th className="pb-3 pr-4">AI Likelihood</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/30 transition-colors group">
                    <td className="py-3.5 pr-4 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                      {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-3.5 pr-4 font-medium text-slate-200 max-w-xs truncate">
                      <span title={item.subject}>{item.subject || 'Untitled'}</span>
                      <span className="block font-mono text-[10px] text-slate-500 truncate">
                        ID: {item.id}
                      </span>
                    </td>
                    <td className="py-3.5 pr-4 text-slate-300 max-w-[200px] truncate">
                      <span title={item.sender}>{item.sender}</span>
                      <span className="block font-mono text-[10px] text-slate-500">
                        {item.sender_domain}
                      </span>
                    </td>
                    <td className="py-3.5 pr-4 whitespace-nowrap">
                      {getSeverityBadge(item.severity, item.risk_score)}
                    </td>
                    <td className="py-3.5 pr-4 whitespace-nowrap font-mono text-[11px] text-purple-300">
                      {Math.round(Number(item.ai_generated_likelihood || 0) * 100)}%
                    </td>
                    <td className="py-3.5 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleInspect(item.id)}
                          className="px-2.5 py-1 rounded bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border border-blue-500/20 text-[11px] font-medium transition-colors inline-flex items-center gap-1"
                        >
                          <ExternalLink className="w-3 h-3" />
                          <span>Inspect</span>
                        </button>
                        <a
                          href={api.getPdfDownloadUrl(item.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px] font-medium transition-colors inline-flex items-center gap-1"
                        >
                          <FileDown className="w-3 h-3" />
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
