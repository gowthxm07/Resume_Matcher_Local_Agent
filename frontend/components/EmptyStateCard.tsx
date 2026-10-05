import { ReactNode } from "react";
import { Clock, ArrowRight } from "lucide-react";

interface EmptyStateCardProps {
  title: string;
  description: string;
  icon: ReactNode;
  phase?: number;
  plannedFeatures: string[];
}

export default function EmptyStateCard({
  title,
  description,
  icon,
  phase = 2,
  plannedFeatures,
}: EmptyStateCardProps) {
  return (
    <div className="p-6 rounded-xl bg-surface border border-surface-border flex flex-col justify-between hover:border-slate-700 transition-colors">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            {icon}
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-slate-400 text-xs font-mono">
            <Clock className="w-3 h-3 text-indigo-400" />
            <span>Phase {phase}</span>
          </div>
        </div>

        <h3 className="text-base font-semibold text-white mb-1.5">{title}</h3>
        <p className="text-xs text-slate-400 mb-4 leading-relaxed">{description}</p>

        <div className="space-y-1.5 pt-3 border-t border-slate-800/80">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">
            Planned Capabilities:
          </div>
          {plannedFeatures.map((feat, idx) => (
            <div key={idx} className="flex items-center gap-2 text-xs text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500/60"></span>
              <span>{feat}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 pt-3 border-t border-slate-800 flex items-center justify-between">
        <span className="text-[11px] text-slate-500 font-mono">
          Architecture Foundation Ready
        </span>
        <div className="flex items-center gap-1 text-xs text-indigo-400 font-medium opacity-60">
          <span>Phase {phase} Scope</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
}
