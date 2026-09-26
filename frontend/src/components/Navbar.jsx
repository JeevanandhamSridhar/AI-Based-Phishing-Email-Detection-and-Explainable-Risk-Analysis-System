import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  History, 
  Cpu, 
  GraduationCap, 
  Wifi, 
  WifiOff, 
  Lock, 
  HardDrive 
} from 'lucide-react';
import { api } from '../services/api';

export default function Navbar({ activeTab, setActiveTab }) {
  const [backendHealth, setBackendHealth] = useState({ online: false, checking: true });

  useEffect(() => {
    let mounted = true;
    const checkStatus = async () => {
      try {
        const res = await api.getHealth();
        if (mounted) {
          setBackendHealth({ online: res.status === 'healthy', checking: false });
        }
      } catch (err) {
        if (mounted) {
          setBackendHealth({ online: false, checking: false });
        }
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { id: 'analyze', label: 'Triage & Analyze', icon: ShieldAlert },
    { id: 'history', label: 'Investigation Ledger', icon: History },
    { id: 'performance', label: 'Research & Telemetry', icon: Cpu },
    { id: 'docs', label: 'Academic Framing & Viva', icon: GraduationCap },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-[#070b14]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Title */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('analyze')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 via-indigo-600 to-cyan-500 p-0.5 shadow-lg shadow-blue-500/20 flex items-center justify-center">
              <div className="w-full h-full bg-[#080c14] rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-blue-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-white font-['Outfit']">PhishGuard</span>
                <span className="text-[10px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold">
                  SOC Triage
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Explainable Risk & Forensic Telemetry</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Invariant & Health Indicators */}
          <div className="flex items-center gap-2.5">
            {/* Defensive Mode Badge */}
            <div 
              title="Defensive Invariant: Zero URL visiting, zero attachment execution, fully offline static inspection"
              className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-mono"
            >
              <Lock className="w-3 h-3 text-emerald-400" />
              <span>DEFENSIVE STATIC</span>
            </div>

            {/* Localhost Badge */}
            <div 
              title="Local execution: All inference, SHAP, and SQLite storage strictly on localhost"
              className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-slate-300 text-[11px] font-mono"
            >
              <HardDrive className="w-3 h-3 text-cyan-400" />
              <span>LOCAL-FIRST</span>
            </div>

            {/* Backend Connectivity Status */}
            <div 
              title={backendHealth.online ? 'Backend API operational on localhost:8000' : 'Backend API disconnected'}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono border ${
                backendHealth.online
                  ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                  : 'bg-red-500/10 border-red-500/20 text-red-400'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${backendHealth.online ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
              <span className="font-semibold">{backendHealth.online ? 'API READY' : 'OFFLINE'}</span>
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
                className={`flex flex-col items-center gap-1 py-1 px-2 text-[10px] font-medium rounded-md ${
                  isActive ? 'text-blue-400 font-semibold' : 'text-slate-400'
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label.split(' ')[0]}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
