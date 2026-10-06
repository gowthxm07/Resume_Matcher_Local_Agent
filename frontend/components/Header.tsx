"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { fetchLocalAgentHealth, fetchSystemStatus } from "@/lib/api";
import { AgentHealthResponse, SystemStatusResponse } from "@/types";
import {
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  HardDrive,
  Shield,
  Bot,
} from "lucide-react";

export default function Header() {
  const [agentHealth, setAgentHealth] = useState<AgentHealthResponse | null>(null);
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const checkStatus = async () => {
    try {
      setRefreshing(true);
      const [agentRes, sysRes] = await Promise.allSettled([
        fetchLocalAgentHealth(),
        fetchSystemStatus(),
      ]);

      if (agentRes.status === "fulfilled") {
        setAgentHealth(agentRes.value);
      } else {
        setAgentHealth(null);
      }

      if (sysRes.status === "fulfilled") {
        setStatus(sysRes.value);
      } else {
        setStatus(null);
      }
    } catch {
      setAgentHealth(null);
      setStatus(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const agentConnected = agentHealth?.status === "ready";
  const ollamaOk = status?.ollama.reachable && status?.ollama.model_exists;
  const dbOk = status?.database.connected;

  return (
    <header className="h-16 border-b border-surface-border bg-surface/80 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-3">
        {/* Local Agent Persistent Indicator */}
        <Link
          href="/get-started"
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-mono font-medium transition-all ${
            agentConnected
              ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300 hover:bg-emerald-900/40"
              : "bg-red-950/40 border-red-500/40 text-red-300 hover:bg-red-900/40 animate-pulse"
          }`}
          title="Click to view Local Agent compatibility diagnostics"
        >
          {agentConnected ? (
            <>
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>LOCAL AGENT CONNECTED</span>
              <span className="text-[10px] text-emerald-500 font-mono">v{agentHealth?.version}</span>
            </>
          ) : (
            <>
              <span className="w-2 h-2 rounded-full bg-red-400"></span>
              <span>LOCAL AGENT OFFLINE</span>
              <span className="text-[10px] underline ml-1">Setup</span>
            </>
          )}
        </Link>
      </div>

      <div className="flex items-center gap-3">
        {/* Ollama Status Pill */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-xs font-mono">
          <Bot className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-400">LLM:</span>
          <span className="text-slate-200">llama3.2:3b</span>
          {ollamaOk ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
          )}
        </div>

        {/* Database Status Pill */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-xs font-mono">
          <HardDrive className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-400">DB:</span>
          <span className="text-slate-200">SQLite</span>
          {dbOk ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <AlertCircle className="w-3.5 h-3.5 text-red-400" />
          )}
        </div>

        {/* Privacy Center Link Pill */}
        <Link
          href="/privacy"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-950/40 border border-indigo-800/60 text-xs font-mono text-indigo-300 hover:bg-indigo-900/40 transition-colors"
          title="Privacy Architecture Center"
        >
          <Shield className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden lg:inline">Privacy: 100% Local</span>
        </Link>

        {/* Refresh button */}
        <button
          onClick={checkStatus}
          disabled={refreshing}
          className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800/60 text-slate-400 hover:text-slate-200 transition-colors"
          title="Refresh System Status"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
        </button>
      </div>
    </header>
  );
}
