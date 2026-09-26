import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  History, 
  Activity, 
  Lock, 
  HardDrive,
  Cpu,
  Radio
} from 'lucide-react';
import { api } from '../services/api';

export default function Navbar({ activeTab, setActiveTab }) {
  const [backendHealth, setBackendHealth] = useState({ online: false, checking: true, latency: null });

  useEffect(() => {
    let mounted = true;
    const checkStatus = async () => {
      const start = performance.now();
      try {
        const res = await api.getHealth();
        const duration = Math.round(performance.now() - start);
        if (mounted) {
          setBackendHealth({ online: res.status === 'healthy', checking: false, latency: duration });
        }
      } catch (err) {
        if (mounted) {
          setBackendHealth({ online: false, checking: false, latency: null });
        }
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 12000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { id: 'analyze', label: 'Triage & Workspace', icon: ShieldAlert, badge: 'Live' },
    { id: 'history', label: 'Investigation Ledger', icon: History },
    { id: 'performance', label: 'Research & Telemetry', icon: Activity, badge: 'Metrics' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-[#060913]/90 backdrop-blur-xl shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Title */}
          <div 
            className="flex items-center gap-3 cursor-pointer group select-none" 
            onClick={() => setActiveTab('analyze')}
          >
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 p-0.5 shadow-lg shadow-blue-500/25 group-hover:shadow-blue-500/40 transition-all duration-300">
                <div className="w-full h-full bg-[#070b16] rounded-[10px] flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform duration-300" />
                </div>
              </div>
              <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
              </span>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight text-white font-['Outfit'] group-hover:text-cyan-300 transition-colors">
                  PhishGuard
                </span>
                <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full bg-blue-500/10 text-cyan-400 border border-cyan-500/30 font-bold shadow-sm">
                  SOC Triage
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block font-mono">
                Explainable Email Threat Intelligence
              </p>
            </div>
          </div>

          {/* Streamlined Operational Tabs */}
          <nav className="hidden md:flex items-center gap-1.5 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800/90 shadow-inner">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`relative flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className={`text-[9px] font-mono uppercase px-1.5 py-0.2 rounded ${
                      isActive ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                  {isActive && (
                    <span className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-8 h-0.5 bg-cyan-400 rounded-full shadow-[0_0_8px_#22d3ee]"></span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Live API Health & Telemetry Status */}
          <div className="flex items-center gap-2">
            <div 
              title={backendHealth.online ? `FastAPI Backend Operational (Response time: ${backendHealth.latency}ms)` : 'Backend Offline'}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-mono border transition-all ${
                backendHealth.online
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 shadow-sm'
                  : 'bg-red-500/10 border-red-500/30 text-red-400'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${backendHealth.online ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
              <span className="font-semibold">
                {backendHealth.online ? `API: ${backendHealth.latency || '<1'}ms` : 'API OFFLINE'}
              </span>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Row */}
        <div className="flex md:hidden items-center justify-around py-2 border-t border-slate-800/60">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex flex-col items-center gap-1 py-1 px-3 text-[11px] font-medium rounded-lg transition-colors ${
                  isActive ? 'text-cyan-400 font-bold bg-blue-500/10' : 'text-slate-400'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
