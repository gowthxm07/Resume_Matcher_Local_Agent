"use client";

import { useState, useEffect } from "react";
import { fetchSystemStatus } from "@/lib/api";
import { SystemStatusResponse } from "@/types";
import {
  Activity,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  HardDrive,
  Shield,
  Bot,
} from "lucide-react";

export default function Header() {
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const checkStatus = async () => {
    try {
      setRefreshing(true);
      const data = await fetchSystemStatus();
      setStatus(data);
    } catch {
      setStatus(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const ollamaOk = status?.ollama.reachable && status?.ollama.model_exists;
  const dbOk = status?.database.connected;
  const vsOk = status?.vector_store.status === "healthy";

  return (
    <header className="h-16 border-b border-surface-border bg-surface/80 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <span className="text-xs font-mono uppercase tracking-widest text-slate-500">
          CareerCrew Core
        </span>
        <span className="text-slate-600">/</span>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-medium text-slate-300">Phase 1 Architecture Active</span>
        </div>
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

        {/* Offline Guard Pill */}
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-950/40 border border-emerald-800/60 text-xs font-mono text-emerald-300">
          <Shield className="w-3.5 h-3.5 text-emerald-400" />
          <span className="hidden lg:inline">Offline Ready</span>
        </div>

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
