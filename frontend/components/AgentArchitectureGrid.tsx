"use client";

import { useState, useEffect } from "react";
import { fetchAgentArchitecture } from "@/lib/api";
import { AgentArchitectureSummary } from "@/types";
import {
  Users,
  ShieldAlert,
  Bot,
  Terminal,
  Workflow,
  Sparkles,
  Search,
  CheckCircle,
} from "lucide-react";

export default function AgentArchitectureGrid() {
  const [data, setData] = useState<AgentArchitectureSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchAgentArchitecture()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-6 rounded-xl bg-surface border border-surface-border animate-pulse">
        <div className="h-6 w-64 bg-slate-800 rounded mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-800/60 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  const agents = data?.agents || [];
  const stages = data?.pipeline_stages || [];

  return (
    <div className="p-6 rounded-xl bg-surface border border-surface-border shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b border-surface-border gap-2">
        <div>
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-semibold text-white">
              Multi-Agent Crew Architecture
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            9 specialized CrewAI agents running locally via Ollama Llama 3.2:3b
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs px-2.5 py-1 rounded-md bg-indigo-950/60 border border-indigo-800/60 text-indigo-300 font-mono">
            Orchestrator: CrewAI (Local LLM)
          </span>
        </div>
      </div>

      {/* Execution Stages flow */}
      <div className="mb-6 p-4 rounded-lg bg-slate-900/60 border border-slate-800">
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
          <Workflow className="w-4 h-4 text-indigo-400" />
          <span>Planned Pipeline Stages</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {stages.map((stage) => (
            <div
              key={stage.stage}
              className="p-3 rounded-md bg-slate-950/60 border border-slate-800/90 text-xs"
            >
              <div className="font-mono text-[10px] text-indigo-400 font-semibold mb-1">
                STAGE {stage.stage}
              </div>
              <div className="font-semibold text-slate-200 mb-2">{stage.name}</div>
              <div className="space-y-1">
                {stage.agents.map((agentName, idx) => (
                  <div key={idx} className="text-[11px] text-slate-400 flex items-center gap-1.5 truncate">
                    <span className="w-1 h-1 rounded-full bg-slate-500"></span>
                    <span>{agentName}</span>
                  </div>
                ))}
              </div>
              {stage.loop_guardrail && (
                <div className="mt-2 pt-2 border-t border-slate-800/60 text-[10px] text-emerald-400 font-mono">
                  Guardrail: {stage.loop_guardrail}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <div
            key={agent.role}
            className="p-4 rounded-lg bg-slate-900/40 border border-slate-800/80 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-semibold text-indigo-400">
                  {agent.role}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                  Phase {agent.phase}
                </span>
              </div>
              <h4 className="text-sm font-semibold text-slate-100 mb-1">{agent.name}</h4>
              <p className="text-xs text-slate-400 mb-3 line-clamp-2">{agent.goal}</p>
            </div>

            <div className="pt-2 border-t border-slate-800/60 text-[11px] text-slate-500 font-mono flex items-center justify-between">
              <span>Model: {agent.llm_model}</span>
              <span>{agent.planned_tools.length} planned tools</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
