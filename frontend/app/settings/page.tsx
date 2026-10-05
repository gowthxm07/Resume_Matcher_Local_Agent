"use client";

import { useState, useEffect } from "react";
import { fetchSystemStatus } from "@/lib/api";
import { SystemStatusResponse } from "@/types";
import { Settings, ShieldCheck, Cpu, HardDrive, Layers, Server } from "lucide-react";

export default function SettingsPage() {
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);

  useEffect(() => {
    fetchSystemStatus().then(setStatus).catch(() => setStatus(null));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-indigo-400" />
            System Configuration
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Local-only execution parameters and privacy audit
          </p>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800 text-emerald-400 text-xs font-mono">
          <ShieldCheck className="w-4 h-4" />
          <span>Zero External API Keys Configured</span>
        </div>
      </div>

      <div className="space-y-4">
        {/* LLM Inference Provider */}
        <div className="p-6 rounded-xl bg-surface border border-surface-border">
          <div className="flex items-center gap-2 mb-3">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <h2 className="text-sm font-semibold text-white">Local LLM Configuration</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">LLM PROVIDER</span>
              <span className="text-indigo-300 font-semibold">Ollama (Strict Local Only)</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">BASE URL</span>
              <span className="text-slate-300">{status?.ollama.base_url || "http://localhost:11434"}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">PRIMARY INFERENCE MODEL</span>
              <span className="text-slate-200 font-semibold">{status?.ollama.configured_model || "llama3.2:3b"}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">LOCAL EMBEDDING MODEL</span>
              <span className="text-slate-200 font-semibold">{status?.ollama.embed_model || "nomic-embed-text"}</span>
            </div>
          </div>
        </div>

        {/* Database & Storage */}
        <div className="p-6 rounded-xl bg-surface border border-surface-border">
          <div className="flex items-center gap-2 mb-3">
            <HardDrive className="w-5 h-5 text-indigo-400" />
            <h2 className="text-sm font-semibold text-white">Local Storage & Vector Store</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">DATABASE ENGINE</span>
              <span className="text-slate-200">SQLite 3 (Local persistent disk file)</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">VECTOR STORE</span>
              <span className="text-slate-200 uppercase">{status?.vector_store.store_type || "ChromaDB"}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 md:col-span-2">
              <span className="text-slate-500 block text-[10px]">PERSISTENCE DIRECTORY</span>
              <span className="text-slate-400 text-[11px] truncate block">
                {status?.vector_store.storage_path || "./data/embeddings/chroma"}
              </span>
            </div>
          </div>
        </div>

        {/* Cloud Security Policy */}
        <div className="p-6 rounded-xl bg-surface border border-surface-border">
          <div className="flex items-center gap-2 mb-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h2 className="text-sm font-semibold text-white">Privacy & Air-Gap Compliance</h2>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            CareerCrew enforces architectural validation at startup: any configuration attempting to load external cloud providers (such as OpenAI, Anthropic, or Gemini) is immediately rejected by the configuration layer. Resumes, code evidence, and personal telemetry never leave this machine.
          </p>
        </div>
      </div>
    </div>
  );
}
