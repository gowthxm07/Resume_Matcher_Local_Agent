"use client";

import { useState, useEffect } from "react";
import { fetchCompatibility, fetchLocalAgentHealth } from "@/lib/api";
import { CompatibilityResponse, AgentHealthResponse, CompatibilityCheckItem } from "@/types";
import { CheckCircle2, XCircle, AlertTriangle, RefreshCw, X, Shield, Terminal, Copy, Check } from "lucide-react";

interface CompatibilityModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CompatibilityModal({ isOpen, onClose }: CompatibilityModalProps) {
  const [report, setReport] = useState<CompatibilityResponse | null>(null);
  const [health, setHealth] = useState<AgentHealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  const loadDiagnostics = async () => {
    try {
      setLoading(true);
      const [compRes, healthRes] = await Promise.allSettled([
        fetchCompatibility(),
        fetchLocalAgentHealth(),
      ]);
      if (compRes.status === "fulfilled") setReport(compRes.value);
      if (healthRes.status === "fulfilled") setHealth(healthRes.value);
    } catch {
      // Handled gracefully in UI
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadDiagnostics();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
      return () => window.removeEventListener("keydown", handleKeyDown);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const allReady = report?.ready === true && health?.status === "ready";

  const copyCommand = (cmd: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedCmd(cmd);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-xl bg-surface border border-surface-border rounded-xl shadow-xl overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="compatibility-modal-title"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className={`w-2.5 h-2.5 rounded-full ${allReady ? "bg-emerald-400" : "bg-amber-400"}`} />
            <h2 id="compatibility-modal-title" className="text-base font-semibold text-white">
              Local Agent Compatibility
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadDiagnostics}
              disabled={loading}
              className="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-surface-hover transition-colors"
              title="Re-check Compatibility"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-surface-hover transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-sm">
          {/* Status Banner */}
          <div
            className={`p-3.5 rounded-lg border text-xs font-mono flex items-center justify-between ${
              allReady
                ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-300"
                : "bg-amber-950/20 border-amber-500/30 text-amber-300"
            }`}
          >
            <div className="flex items-center gap-2 font-medium">
              {allReady ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>COMPATIBILITY CHECK OK</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>COMPATIBILITY CHECK FAILED</span>
                </>
              )}
            </div>
            <span className="text-zinc-400 text-[11px] font-sans">
              127.0.0.1:8000 &bull; {health ? `v${health.version}` : "offline"}
            </span>
          </div>

          {/* Checks List */}
          <div className="space-y-2">
            <div className="text-xs font-medium uppercase tracking-wider text-zinc-400 px-0.5">
              Verified Components
            </div>

            <div className="border border-surface-border rounded-lg divide-y divide-surface-border bg-background/50">
              {report?.checks && report.checks.length > 0 ? (
                report.checks.map((item: CompatibilityCheckItem, idx: number) => {
                  const isOk = item.status === "READY";
                  return (
                    <div key={idx} className="p-3 flex items-start justify-between gap-3 text-xs">
                      <div className="flex items-start gap-2.5">
                        {isOk ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                        )}
                        <div>
                          <div className="font-medium text-white flex items-center gap-2">
                            <span>{item.name}</span>
                            {item.detected_version && (
                              <span className="text-[10px] text-zinc-400 font-mono">
                                ({item.detected_version})
                              </span>
                            )}
                          </div>
                          <p className="text-zinc-400 text-[11px] mt-0.5">{item.message}</p>
                        </div>
                      </div>

                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                          isOk
                            ? "bg-emerald-950/40 border-emerald-500/30 text-emerald-300"
                            : "bg-red-950/40 border-red-500/30 text-red-300"
                        }`}
                      >
                        {item.status.toUpperCase()}
                      </span>
                    </div>
                  );
                })
              ) : (
                <div className="p-4 text-center text-xs text-zinc-500">
                  {loading ? "Checking local system components..." : "No compatibility checks reported"}
                </div>
              )}
            </div>
          </div>

          {/* Quick Remediation if any check fails */}
          {!allReady && (
            <div className="p-3.5 rounded-lg border border-surface-border bg-surface-hover/50 space-y-2 text-xs">
              <div className="font-medium text-zinc-200 flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5 text-zinc-400" />
                <span>Quick Setup Commands</span>
              </div>
              <div className="space-y-1.5 font-mono text-[11px]">
                {[
                  "ollama pull llama3.2:3b",
                  "ollama pull nomic-embed-text",
                  "uvicorn backend.app.main:app --port 8000",
                ].map((cmd) => (
                  <div
                    key={cmd}
                    className="flex items-center justify-between p-2 rounded bg-background border border-surface-border text-zinc-300"
                  >
                    <code>{cmd}</code>
                    <button
                      onClick={() => copyCommand(cmd)}
                      className="p-1 hover:text-white text-zinc-500"
                      title="Copy command"
                    >
                      {copiedCmd === cmd ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-surface-border bg-surface-hover/20 flex items-center justify-between text-xs">
          <div className="flex items-center gap-1.5 text-zinc-400 font-mono text-[11px]">
            <Shield className="w-3.5 h-3.5 text-indigo-400" />
            <span>Strict 127.0.0.1 binding &bull; Zero Cloud AI</span>
          </div>
          <button
            onClick={loadDiagnostics}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white font-medium transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Re-check Compatibility</span>
          </button>
        </div>
      </div>
    </div>
  );
}
