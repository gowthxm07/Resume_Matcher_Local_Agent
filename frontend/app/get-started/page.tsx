"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Terminal,
  ShieldCheck,
  Cpu,
  ArrowRight,
  Copy,
  Check,
  Download,
  AlertCircle,
  Info,
  Server,
  Code2,
} from "lucide-react";
import { fetchCompatibility, fetchLocalAgentHealth } from "@/lib/api";
import { CompatibilityResponse, CompatibilityCheckItem, AgentHealthResponse } from "@/types";

export default function GetStartedPage() {
  const [report, setReport] = useState<CompatibilityResponse | null>(null);
  const [health, setHealth] = useState<AgentHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [rechecking, setRechecking] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [activeOs, setActiveOs] = useState<"windows" | "macos" | "linux">("windows");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const runDiagnostics = async () => {
    try {
      setRechecking(true);
      setErrorMsg(null);
      const [compRes, healthRes] = await Promise.allSettled([
        fetchCompatibility(),
        fetchLocalAgentHealth(),
      ]);

      if (compRes.status === "fulfilled") {
        setReport(compRes.value);
      } else {
        setReport(null);
        setErrorMsg("Could not connect to CareerCrew Local Agent at http://127.0.0.1:8000. Is the agent running?");
      }

      if (healthRes.status === "fulfilled") {
        setHealth(healthRes.value);
      } else {
        setHealth(null);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to run diagnostics");
    } finally {
      setLoading(false);
      setRechecking(false);
    }
  };

  useEffect(() => {
    runDiagnostics();
  }, []);

  const copyCommand = (cmd: string, idx: number) => {
    navigator.clipboard.writeText(cmd);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const missingCount = report?.checks.filter((c) => c.required && c.status !== "READY").length || 0;
  const isReady = report?.ready === true;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "READY":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
            <CheckCircle2 className="w-3.5 h-3.5" /> READY
          </span>
        );
      case "MISSING":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-950/60 text-red-400 border border-red-800/60">
            <XCircle className="w-3.5 h-3.5" /> MISSING
          </span>
        );
      case "OUTDATED":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-950/60 text-amber-400 border border-amber-800/60">
            <AlertTriangle className="w-3.5 h-3.5" /> OUTDATED
          </span>
        );
      case "OPTIONAL":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-900 text-slate-400 border border-slate-700">
            <Info className="w-3.5 h-3.5" /> OPTIONAL
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-950/60 text-rose-400 border border-rose-800/60">
            <AlertCircle className="w-3.5 h-3.5" /> ERROR
          </span>
        );
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto p-4 sm:p-6 pb-12">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors font-mono"
      >
        <span>&larr; Back to CareerCrew Agent</span>
      </Link>

      {/* Header Banner */}
      <div className="border border-surface-border rounded-xl bg-surface/60 backdrop-blur p-6 sm:p-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/50 border border-indigo-800/50 text-indigo-300 text-xs font-mono">
              <Cpu className="w-3.5 h-3.5" />
              <span>CareerCrew Local Agent Architecture</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              Get Started with CareerCrew
            </h1>
            <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
              CareerCrew is designed as a <strong className="text-slate-200">privacy-first local intelligence agent</strong>.
              Whether viewing this dashboard on Vercel or locally, all resumes, job descriptions, Git codebases,
              and AI reasoning remain 100% on your machine.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row md:flex-col gap-3 shrink-0">
            <button
              onClick={runDiagnostics}
              disabled={rechecking}
              className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-colors shadow-lg shadow-indigo-600/20 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${rechecking ? "animate-spin" : ""}`} />
              <span>Re-check Compatibility</span>
            </button>
            <Link
              href="/privacy"
              className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-800 transition-colors"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>View Privacy Center</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Connection & Compatibility Banner */}
      {errorMsg ? (
        <div className="border border-red-800/60 bg-red-950/30 rounded-xl p-6 text-red-300 space-y-4">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-red-900/40 border border-red-700/50 shrink-0">
              <XCircle className="w-6 h-6 text-red-400" />
            </div>
            <div className="space-y-1">
              <h2 className="text-lg font-bold text-white">Local Agent Offline</h2>
              <p className="text-sm text-red-200/90 leading-relaxed">
                The CareerCrew Local Agent is not responding at <code className="px-1.5 py-0.5 rounded bg-red-950 border border-red-800 font-mono text-xs">http://127.0.0.1:8000</code>.
                Start your local agent runtime using the instructions below, then click <strong>Re-check Compatibility</strong>.
              </p>
            </div>
          </div>
        </div>
      ) : isReady ? (
        <div className="border border-emerald-800/60 bg-emerald-950/30 rounded-xl p-6 text-emerald-300 space-y-4 shadow-lg shadow-emerald-950/30">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start sm:items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-900/40 border border-emerald-700/50 shrink-0">
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <span>COMPATIBILITY CHECK OK</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-900/80 text-emerald-300 font-mono">
                    All Required Ready
                  </span>
                </h2>
                <p className="text-sm text-emerald-200/90 mt-0.5">
                  Your system is verified and ready to run CareerCrew locally with zero cloud dependencies.
                </p>
              </div>
            </div>

            <Link
              href="/projects"
              className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm transition-colors shadow-md shadow-emerald-600/30 shrink-0"
            >
              <span>Continue to CareerCrew</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-emerald-800/40 text-xs font-mono text-emerald-200">
            <div>AI Inference: <strong className="text-white">LOCAL (Ollama)</strong></div>
            <div>Data Processing: <strong className="text-white">LOCAL</strong></div>
            <div>Code Scanning: <strong className="text-white">LOCAL (Git)</strong></div>
            <div>Database: <strong className="text-white">LOCAL (SQLite)</strong></div>
          </div>
        </div>
      ) : (
        <div className="border border-amber-800/60 bg-amber-950/30 rounded-xl p-6 text-amber-300 space-y-3">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0" />
            <div>
              <h2 className="text-lg font-bold text-white">
                COMPATIBILITY CHECK FAILED ({missingCount} required {missingCount === 1 ? "component" : "components"} need attention)
              </h2>
              <p className="text-sm text-amber-200/90 mt-0.5">
                Install or start the missing local components below, then click Re-check Compatibility.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Diagnostics Table */}
      <div className="border border-surface-border rounded-xl bg-surface overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-indigo-400" />
            <h2 className="font-semibold text-white text-base">System Compatibility Diagnostics</h2>
          </div>
          {report && (
            <span className="text-xs text-slate-400 font-mono">
              Agent Protocol v{report.agent_version} • Checked: {new Date(report.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
            <span>Scanning local runtime environment...</span>
          </div>
        ) : report ? (
          <div className="divide-y divide-surface-border overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900/60 text-xs text-slate-400 uppercase font-mono tracking-wider">
                <tr>
                  <th className="px-6 py-3">Component</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Detected Version</th>
                  <th className="px-6 py-3">Requirement</th>
                  <th className="px-6 py-3">Diagnostic Message</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border">
                {report.checks.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/20 transition-colors">
                    <td className="px-6 py-4 font-medium text-white flex items-center gap-2">
                      <span>{item.name}</span>
                      {item.required && (
                        <span className="text-[10px] text-indigo-400 font-mono font-normal">(Required)</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(item.status)}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-300">
                      {item.detected_version || <span className="text-slate-500">—</span>}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-400">
                      {item.required_version || "Any"}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-300 leading-relaxed max-w-md">
                      {item.message}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400 text-sm">
            Diagnostics unavailable because the Local Agent is offline.
          </div>
        )}
      </div>

      {/* OS Setup Instructions */}
      <div className="border border-surface-border rounded-xl bg-surface p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-indigo-400" />
              <h2 className="font-semibold text-white text-base">Setup & Remediation Guide</h2>
            </div>
            <p className="text-xs text-slate-400">
              Run these commands locally to satisfy any missing requirements.
            </p>
          </div>

          {/* OS Switcher */}
          <div className="inline-flex rounded-lg bg-slate-900 p-1 border border-slate-800 self-start sm:self-auto">
            {(["windows", "macos", "linux"] as const).map((os) => (
              <button
                key={os}
                onClick={() => setActiveOs(os)}
                className={`px-3 py-1 rounded text-xs font-medium capitalize transition-colors ${
                  activeOs === os
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {os}
              </button>
            ))}
          </div>
        </div>

        {/* Step-by-Step Instructions */}
        <div className="space-y-6">
          {/* Step 1: Ollama & Models */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
              <span className="w-5 h-5 rounded-full bg-indigo-600/30 text-indigo-400 border border-indigo-500/30 flex items-center justify-center text-xs">
                1
              </span>
              <span>Install Ollama & Required Models</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Ollama runs local LLMs entirely offline on your GPU or CPU without telemetry or external APIs.
            </p>

            <div className="space-y-2">
              {[
                {
                  label: "Pull Llama 3.2:3B inference model",
                  cmd: "ollama pull llama3.2:3b",
                },
                {
                  label: "Pull nomic-embed-text local embedding model",
                  cmd: "ollama pull nomic-embed-text",
                },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-lg px-4 py-2.5 font-mono text-xs text-slate-300"
                >
                  <div className="flex items-center gap-3 truncate">
                    <span className="text-slate-500 select-none">$</span>
                    <span className="text-emerald-300 truncate">{item.cmd}</span>
                  </div>
                  <button
                    onClick={() => copyCommand(item.cmd, idx)}
                    className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors shrink-0 ml-2"
                    title="Copy command"
                  >
                    {copiedIndex === idx ? (
                      <Check className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Step 2: Start Local Agent */}
          <div className="space-y-3 pt-4 border-t border-surface-border">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
              <span className="w-5 h-5 rounded-full bg-indigo-600/30 text-indigo-400 border border-indigo-500/30 flex items-center justify-center text-xs">
                2
              </span>
              <span>Run the CareerCrew Local Agent</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Run this in your terminal inside the <code className="text-slate-300 font-mono">backend</code> directory:
            </p>

            <div className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-lg px-4 py-2.5 font-mono text-xs text-slate-300">
              <div className="flex items-center gap-3 truncate">
                <span className="text-slate-500 select-none">$</span>
                <span className="text-indigo-300 truncate">
                  uvicorn app.main:app --host 127.0.0.1 --port 8000
                </span>
              </div>
              <button
                onClick={() =>
                  copyCommand("uvicorn app.main:app --host 127.0.0.1 --port 8000", 99)
                }
                className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors shrink-0 ml-2"
                title="Copy command"
              >
                {copiedIndex === 99 ? (
                  <Check className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Step 3: Git CLI */}
          <div className="space-y-3 pt-4 border-t border-surface-border">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
              <span className="w-5 h-5 rounded-full bg-indigo-600/30 text-indigo-400 border border-indigo-500/30 flex items-center justify-center text-xs">
                3
              </span>
              <span>Git Evidence Scanner</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Ensure Git is installed and available in your system PATH so CareerCrew can safely audit local commits and code evidence.
            </p>
            <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs text-slate-400">
              {activeOs === "windows" && "Windows: Install Git for Windows from https://git-scm.com or 'winget install Git.Git'."}
              {activeOs === "macos" && "macOS: Install via Xcode Command Line Tools ('xcode-select --install') or 'brew install git'."}
              {activeOs === "linux" && "Linux: Install via 'sudo apt-get install git' or distribution package manager."}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
