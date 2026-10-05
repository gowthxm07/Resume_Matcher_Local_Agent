import { Sparkles, Clock, Cpu } from "lucide-react";

export default function AnalysisPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            Multi-Agent Analysis Engine
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Zero-hallucination iterative optimization loop and interview intelligence
          </p>
        </div>
        <div className="px-3 py-1 rounded-full bg-slate-800 text-slate-400 text-xs font-mono border border-slate-700">
          Phase 2 Component
        </div>
      </div>

      <div className="p-8 rounded-xl bg-surface border border-surface-border text-center max-w-xl mx-auto my-12">
        <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-4 border border-indigo-500/20">
          <Cpu className="w-6 h-6" />
        </div>
        <h2 className="text-base font-semibold text-white mb-2">
          CrewAI Orchestration Blueprint Established
        </h2>
        <p className="text-xs text-slate-400 leading-relaxed mb-6">
          The 9-agent CrewAI architecture, SQLite model (<code className="text-indigo-300">analysis_runs</code>), and local Ollama inference service are fully connected. The iterative optimizer loop, Fact Checker guardrail, and Interview Agent activate in Phase 2.
        </p>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-400 font-mono">
          <Clock className="w-3.5 h-3.5 text-indigo-400" />
          <span>Scheduled for Phase 2 Implementation</span>
        </div>
      </div>
    </div>
  );
}
