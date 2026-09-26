import React from 'react';
import { AlertOctagon, AlertTriangle, Info, CheckCircle2, Shield } from 'lucide-react';

export default function RiskMeter({ score = 0, severity = 'LOW', bracket = '0-24' }) {
  // Normalize score
  const safeScore = Math.min(100, Math.max(0, Number(score) || 0));

  // Determine styling based on severity
  const severityConfig = {
    CRITICAL: {
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30',
      glowClass: 'glow-critical',
      strokeColor: '#ef4444',
      badgeText: 'CRITICAL THREAT',
      icon: AlertOctagon,
      action: 'Immediate Quarantine & Credential Revocation Recommended',
      subtext: 'High-confidence indicators of malicious deception or harvesting',
    },
    HIGH: {
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/30',
      glowClass: 'glow-high',
      strokeColor: '#f97316',
      badgeText: 'HIGH RISK',
      icon: AlertTriangle,
      action: 'Block Domain & Escalate to Tier-2 Security Operations',
      subtext: 'Significant authentication anomalies or deceptive patterns detected',
    },
    MODERATE: {
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/30',
      glowClass: 'glow-moderate',
      strokeColor: '#f59e0b',
      badgeText: 'MODERATE RISK',
      icon: Info,
      action: 'Tag External Advisory & Sanitize Suspicious Links',
      subtext: 'Borderline or conflicting authentication/content signals',
    },
    LOW: {
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/30',
      glowClass: 'glow-low',
      strokeColor: '#10b981',
      badgeText: 'LOW RISK / BENIGN',
      icon: CheckCircle2,
      action: 'Allow Delivery with Standard Hygiene Monitoring',
      subtext: 'Authentic cryptographic signatures & benign structural patterns',
    },
  };

  const current = severityConfig[severity] || severityConfig.LOW;
  const Icon = current.icon;

  // Circular gauge calculations
  const radius = 78;
  const circumference = 2 * Math.PI * radius;
  // Use a 270-degree arc for dashboard gauge feel
  const arcLength = circumference * 0.75;
  const strokeDashoffset = arcLength - (safeScore / 100) * arcLength;

  return (
    <div className={`p-6 rounded-2xl bg-slate-900/70 border ${current.borderColor} backdrop-blur-md shadow-xl flex flex-col items-center justify-between transition-all duration-300`}>
      <div className="w-full flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Composite Risk Score</span>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60">
          Bracket: {bracket}
        </span>
      </div>

      {/* Circular Gauge */}
      <div className="relative flex items-center justify-center my-3">
        <svg className="w-48 h-48 transform -rotate-135" viewBox="0 0 200 200">
          {/* Background track arc */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke="#1e293b"
            strokeWidth="14"
            fill="transparent"
            strokeDasharray={arcLength}
            strokeDashoffset="0"
            strokeLinecap="round"
          />
          {/* Colored progress arc */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke={current.strokeColor}
            strokeWidth="14"
            fill="transparent"
            strokeDasharray={arcLength}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            style={{
              filter: `drop-shadow(0 0 6px ${current.strokeColor}88)`,
            }}
          />
        </svg>

        {/* Center score readout */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pt-2">
          <span className={`text-4xl font-extrabold tracking-tight font-['Outfit'] ${current.color}`}>
            {safeScore.toFixed(1)}
          </span>
          <span className="text-[11px] uppercase tracking-widest text-slate-400 font-mono">/ 100</span>
        </div>
      </div>

      {/* Severity verdict & action recommendation */}
      <div className="w-full text-center flex flex-col items-center gap-2 mt-1">
        <div className={`inline-flex items-center gap-2 px-3.5 py-1 rounded-full text-xs font-bold font-mono tracking-wider border ${current.bgColor} ${current.borderColor} ${current.color} ${current.glowClass}`}>
          <Icon className="w-3.5 h-3.5" />
          <span>{current.badgeText}</span>
        </div>

        <p className="text-xs font-medium text-slate-200 mt-1 max-w-sm">
          {current.action}
        </p>
        <p className="text-[11px] text-slate-400 max-w-xs">
          {current.subtext}
        </p>
      </div>
    </div>
  );
}
