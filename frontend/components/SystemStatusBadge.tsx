"use client";

import { SystemStatusResponse } from "@/types";
import {
  CheckCircle2,
  AlertTriangle,
  Server,
  Cpu,
  Database,
  Layers,
  ShieldCheck,
} from "lucide-react";

interface Props {
  status: SystemStatusResponse | null;
  loading: boolean;
}

export default function SystemStatusBadge({ status, loading }: Props) {
  if (loading) {
    return (
      <div className="p-6 rounded-xl bg-surface border border-surface-border animate-pulse">
        <div className="h-5 w-48 bg-slate-800 rounded mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="h-20 bg-slate-800/60 rounded"></div>
          <div className="h-20 bg-slate-800/60 rounded"></div>
          <div className="h-20 bg-slate-800/60 rounded"></div>
          <div className="h-20 bg-slate-800/60 rounded"></div>
        </div>
      </div>
    );
  }

  const ollama = status?.ollama;
  const db = status?.database;
  const vs = status?.vector_store;

  return (
    <div className="p-6 rounded-xl bg-surface border border-surface-border shadow-xl">
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-surface-border">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Server className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Local System Telemetry</h3>
            <p className="text-xs text-slate-400">Real-time status of host services with 0 cloud dependencies</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-emerald-950/40 border border-emerald-800/50 text-emerald-400 text-xs font-mono">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Strict Local Architecture</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Ollama LLM */}
        <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5 font-medium">
              <Cpu className="w-4 h-4 text-indigo-400" /> Local LLM
            </span>
            {ollama?.reachable && ollama.model_exists ? (
              <span className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" /> Ready
              </span>
            ) : (
              <span className="flex items-center gap-1 text-amber-400">
                <AlertTriangle className="w-3.5 h-3.5" /> Offline
              </span>
            )}
          </div>
          <div className="font-mono text-sm text-white font-semibold truncate">
            {ollama?.configured_model || "llama3.2:3b"}
          </div>
          <div className="text-[11px] text-slate-500 mt-2 flex items-center justify-between">
            <span>Latency: {ollama?.latency_ms ? `${ollama.latency_ms}ms` : "N/A"}</span>
            <span className="truncate max-w-[100px]">{ollama?.base_url}</span>
          </div>
        </div>

        {/* Local Embeddings */}
        <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5 font-medium">
              <Layers className="w-4 h-4 text-indigo-400" /> Embeddings
            </span>
            {ollama?.reachable && ollama.embed_model_exists ? (
              <span className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" /> Ready
              </span>
            ) : (
              <span className="flex items-center gap-1 text-amber-400">
                <AlertTriangle className="w-3.5 h-3.5" /> Check
              </span>
            )}
          </div>
          <div className="font-mono text-sm text-white font-semibold truncate">
            {ollama?.embed_model || "nomic-embed-text"}
          </div>
          <div className="text-[11px] text-slate-500 mt-2">
            Local Ollama Vectorizer (0 OpenAI)
          </div>
        </div>

        {/* SQLite Database */}
        <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5 font-medium">
              <Database className="w-4 h-4 text-indigo-400" /> SQLite Storage
            </span>
            {db?.connected ? (
              <span className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" /> Connected
              </span>
            ) : (
              <span className="flex items-center gap-1 text-red-400">
                <AlertTriangle className="w-3.5 h-3.5" /> Disconnected
              </span>
            )}
          </div>
          <div className="font-mono text-sm text-white font-semibold">
            careercrew.db
          </div>
          <div className="text-[11px] text-slate-500 mt-2">
            {db?.tables?.length || 5} core tables initialized
          </div>
        </div>

        {/* Local Vector DB */}
        <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5 font-medium">
              <Layers className="w-4 h-4 text-indigo-400" /> Vector Database
            </span>
            {vs?.status === "healthy" ? (
              <span className="flex items-center gap-1 text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" /> Initialized
              </span>
            ) : (
              <span className="flex items-center gap-1 text-amber-400">
                <AlertTriangle className="w-3.5 h-3.5" /> Ready
              </span>
            )}
          </div>
          <div className="font-mono text-sm text-white font-semibold uppercase">
            {vs?.store_type || "Chroma"}
          </div>
          <div className="text-[11px] text-slate-500 mt-2">
            Persistent disk collection
          </div>
        </div>
      </div>
    </div>
  );
}
