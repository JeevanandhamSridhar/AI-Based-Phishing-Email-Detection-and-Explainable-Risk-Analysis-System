import React from 'react';
import { 
  Cpu, 
  Globe, 
  MailCheck, 
  UserX, 
  MessageSquareWarning, 
  Paperclip, 
  FileCode2, 
  Layers 
} from 'lucide-react';

export default function FactorBreakdown({ factorBreakdown = {} }) {
  // Mapping of factor keys to display metadata
  const factorMeta = {
    ml_phishing: {
      name: 'ML Phishing Probability',
      maxWeight: 30,
      icon: Cpu,
      color: 'bg-blue-500',
      textColor: 'text-blue-400',
      description: 'Supervised Scikit-learn TF-IDF + Logistic Regression classification',
    },
    url_risk: {
      name: 'Static URL Analysis',
      maxWeight: 20,
      icon: Globe,
      color: 'bg-indigo-500',
      textColor: 'text-indigo-400',
      description: 'IP hosts, Punycode, high-risk TLDs, entropy & subdomains',
    },
    header_auth: {
      name: 'Header & Auth Alignment',
      maxWeight: 15,
      icon: MailCheck,
      color: 'bg-purple-500',
      textColor: 'text-purple-400',
      description: 'SPF, DKIM, DMARC alignment & display-name spoofing',
    },
    sender_domain: {
      name: 'Sender Domain Impersonation',
      maxWeight: 10,
      icon: UserX,
      color: 'bg-rose-500',
      textColor: 'text-rose-400',
      description: 'Levenshtein brand typosquatting & homoglyph detection',
    },
    social_engineering: {
      name: 'Social Engineering Cues',
      maxWeight: 10,
      icon: MessageSquareWarning,
      color: 'bg-amber-500',
      textColor: 'text-amber-400',
      description: 'Urgency, fear coercion, financial bait & credential harvesting',
    },
    attachment_risk: {
      name: 'Attachment Metadata Screening',
      maxWeight: 10,
      icon: Paperclip,
      color: 'bg-orange-500',
      textColor: 'text-orange-400',
      description: 'Executable extensions, double extensions & macro hazards',
    },
    content_anomalies: {
      name: 'Content Obfuscation',
      maxWeight: 5,
      icon: FileCode2,
      color: 'bg-cyan-500',
      textColor: 'text-cyan-400',
      description: 'Zero-width unicode, whitespace padding & CSS hidden text',
    },
  };

  const factorKeys = [
    'ml_phishing',
    'url_risk',
    'header_auth',
    'sender_domain',
    'social_engineering',
    'attachment_risk',
    'content_anomalies',
  ];

  return (
    <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-blue-400" />
          <h3 className="font-semibold text-slate-200 text-sm font-['Outfit']">
            Weighted Factor Decomposition (100 pts)
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          7 Independent Signals
        </span>
      </div>

      <div className="space-y-4">
        {factorKeys.map((key) => {
          const meta = factorMeta[key] || {
            name: key,
            maxWeight: 10,
            icon: Layers,
            color: 'bg-slate-500',
            textColor: 'text-slate-400',
            description: '',
          };
          const item = factorBreakdown[key] || {
            weight: meta.maxWeight,
            raw_score: 0,
            weighted_contribution: 0,
            details: {},
          };

          const Icon = meta.icon;
          const pctOfMax = meta.maxWeight > 0 ? (item.weighted_contribution / meta.maxWeight) * 100 : 0;

          return (
            <div key={key} className="group">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <div className="flex items-center gap-2">
                  <div className="p-1 rounded bg-slate-800/80 border border-slate-700/60">
                    <Icon className={`w-3.5 h-3.5 ${meta.textColor}`} />
                  </div>
                  <div>
                    <span className="font-medium text-slate-200 group-hover:text-white transition-colors">
                      {meta.name}
                    </span>
                    <span className="ml-2 text-[10px] font-mono text-slate-400">
                      (w: {item.weight || meta.maxWeight}%)
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 font-mono text-[11px]">
                  <span className="text-slate-400">
                    Raw: <strong className="text-slate-200">{Number(item.raw_score).toFixed(0)}/100</strong>
                  </span>
                  <span className="text-emerald-400 font-semibold bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                    +{Number(item.weighted_contribution).toFixed(1)} pts
                  </span>
                </div>
              </div>

              {/* Visual Progress Bar */}
              <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden flex border border-slate-700/40">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${meta.color}`}
                  style={{ width: `${Math.min(100, Math.max(0, pctOfMax))}%` }}
                />
              </div>

              {/* Subtext description & detail preview */}
              <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
                <span className="truncate max-w-[280px]">{meta.description}</span>
                {item.details && Object.keys(item.details).length > 0 && (
                  <span className="font-mono text-slate-400">
                    {Object.entries(item.details)
                      .slice(0, 1)
                      .map(([k, v]) => `${k}: ${Array.isArray(v) ? (v.length ? v.join(', ') : 'none') : v}`)
                      .join(' | ')}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
