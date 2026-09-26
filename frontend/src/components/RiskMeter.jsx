import React, { useEffect, useState } from 'react';
import { AlertOctagon, AlertTriangle, Info, CheckCircle2, Shield, Activity } from 'lucide-react';

export default function RiskMeter({ score = 0, severity = 'LOW', bracket = '0-24' }) {
  const safeScore = Math.min(100, Math.max(0, Number(score) || 0));
  const [animatedScore, setAnimatedScore] = useState(0);

  // Smooth Count-Up Effect from 0 to score
  useEffect(() => {
    let start = 0;
    const duration = 1000;
    const startTime = performance.now();

    const updateCounter = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(Number((safeScore * easeProgress).toFixed(1)));

      if (progress < 1) {
        requestAnimationFrame(updateCounter);
      }
    };

    requestAnimationFrame(updateCounter);
  }, [safeScore]);

  // Determine styling based on severity
  const severityConfig = {
    CRITICAL: {
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/40',
      glowClass: 'glow-critical',
      strokeColor: '#ef4444',
      badgeText: 'CRITICAL THREAT',
      icon: AlertOctagon,
      action: 'Immediate Quarantine & Credential Revocation Recommended',
      subtext: 'Multiple high-confidence indicators of malicious deception detected',
    },
    HIGH: {
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/40',
      glowClass: 'glow-high',
      strokeColor: '#f97316',
      badgeText: 'HIGH RISK',
      icon: AlertTriangle,
      action: 'Block Domain & Escalate to Security Operations',
      subtext: 'Significant authentication anomalies or deceptive patterns detected',
    },
    MODERATE: {
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/40',
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
      borderColor: 'border-emerald-500/40',
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
  const arcLength = circumference * 0.75;
  const strokeDashoffset = arcLength - (animatedScore / 100) * arcLength;

  return (
    <div className={`p-6 rounded-2xl bg-slate-900/80 border ${current.borderColor} backdrop-blur-xl shadow-2xl flex flex-col items-center justify-between transition-all duration-300 relative overflow-hidden group`}>
      {/* Background radial glow */}
      <div 
        className="absolute -top-10 -right-10 w-40 h-40 rounded-full blur-3xl opacity-20 pointer-events-none transition-all duration-700"
        style={{ backgroundColor: current.strokeColor }}
      />

      <div className="w-full flex items-center justify-between mb-2 relative z-10">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold">
            Composite Threat Score
          </span>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-slate-800/90 text-slate-300 border border-slate-700/60 font-semibold shadow-sm">
          Bracket: {bracket}
        </span>
      </div>

      {/* Circular Gauge */}
      <div className="relative flex items-center justify-center my-3">
        <svg className="w-52 h-52 transform -rotate-135" viewBox="0 0 200 200">
          {/* Background track arc */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            stroke="#131b2e"
            strokeWidth="14"
            fill="transparent"
            strokeDasharray={arcLength}
            strokeDashoffset="0"
            strokeLinecap="round"
          />
          {/* Colored progress arc with glow */}
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
            className="transition-all duration-500 ease-out"
            style={{
              filter: `drop-shadow(0 0 8px ${current.strokeColor}aa)`,
            }}
          />
        </svg>

        {/* Center score readout */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pt-2">
          <span className={`text-5xl font-black tracking-tight font-['Outfit'] ${current.color} drop-shadow-md`}>
            {animatedScore.toFixed(1)}
          </span>
          <span className="text-[11px] uppercase tracking-widest text-slate-400 font-mono mt-0.5">
            / 100 POINTS
          </span>
        </div>
      </div>

      {/* Severity verdict & action recommendation */}
      <div className="w-full text-center flex flex-col items-center gap-2 mt-1 relative z-10">
        <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold font-mono tracking-wider border ${current.bgColor} ${current.borderColor} ${current.color} ${current.glowClass} shadow-lg transition-transform hover:scale-105`}>
          <Icon className="w-4 h-4 animate-pulse" />
          <span>{current.badgeText}</span>
        </div>

        <p className="text-xs font-semibold text-slate-200 mt-1 max-w-sm font-['Outfit']">
          {current.action}
        </p>
        <p className="text-[11px] text-slate-400 max-w-xs leading-normal">
          {current.subtext}
        </p>
      </div>
    </div>
  );
}
