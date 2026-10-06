"use client";

import Link from "next/link";
import {
  ShieldCheck,
  HardDrive,
  Cpu,
  Lock,
  EyeOff,
  Server,
  CheckCircle2,
  AlertCircle,
  FileText,
  GitBranch,
  Database,
  Layers,
  ArrowRight,
  ExternalLink,
} from "lucide-react";

export default function PrivacyPage() {
  const dataArtifacts = [
    {
      name: "Resume Documents (PDF / DOCX)",
      storage: "Local filesystem (data/resumes/)",
      processing: "Local PyMuPDF & python-docx parsers",
      cloudExposure: "NONE (Never transmitted to Vercel or cloud)",
      status: "100% LOCAL",
    },
    {
      name: "Job Descriptions",
      storage: "Local SQLite database",
      processing: "Local regex & heuristic section extractors",
      cloudExposure: "NONE (Kept entirely within local agent)",
      status: "100% LOCAL",
    },
    {
      name: "Git Repositories & Source Code",
      storage: "Your existing local git directories",
      processing: "Local Git CLI & read-only AST scanners",
      cloudExposure: "NONE (Source code never leaves your disk)",
      status: "100% LOCAL",
    },
    {
      name: "Vector Embeddings",
      storage: "Local ChromaDB (data/embeddings/chroma/)",
      processing: "Local Ollama nomic-embed-text model",
      cloudExposure: "NONE (Zero cloud vector store dependencies)",
      status: "100% LOCAL",
    },
    {
      name: "LLM Prompts & Completions",
      storage: "Local SQLite analysis telemetry",
      processing: "Local Ollama Llama 3.2:3B inference",
      cloudExposure: "NONE (Zero OpenAI, Anthropic, or Gemini calls)",
      status: "100% LOCAL",
    },
    {
      name: "Multi-Agent Orchestration",
      storage: "Local memory & SQLite audit log",
      processing: "Local CrewAI OSS framework",
      cloudExposure: "NONE (Orchestration executes purely on localhost)",
      status: "100% LOCAL",
    },
    {
      name: "Resume Versions & Fact Diffs",
      storage: "Local SQLite (resume_versions table)",
      processing: "Deterministic FactChecker & ATSService",
      cloudExposure: "NONE (Version records stored locally)",
      status: "100% LOCAL",
    },
    {
      name: "Vercel Web Dashboard",
      storage: "Browser client-side cache",
      processing: "Next.js UI rendering & layout presentation",
      cloudExposure: "UI ONLY (Stateless client connecting to 127.0.0.1)",
      status: "PRESENTATION ONLY",
    },
  ];

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="border border-surface-border rounded-xl bg-surface/60 backdrop-blur p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/50 border border-emerald-800/50 text-emerald-300 text-xs font-mono">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Zero External Cloud AI APIs</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              CareerCrew Privacy Center
            </h1>
            <p className="text-slate-400 text-sm max-w-2xl leading-relaxed">
              Every design decision in CareerCrew is engineered to protect candidate confidentiality.
              We believe your career history, source code repositories, and job applications belong exclusively to you.
            </p>
          </div>

          <Link
            href="/get-started"
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-colors shadow-lg shadow-indigo-600/20 shrink-0 self-start sm:self-auto"
          >
            <span>Agent Diagnostics</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* Visual Data Flow Architecture Card */}
      <div className="border border-surface-border rounded-xl bg-surface p-6 sm:p-8 space-y-6">
        <div className="space-y-1">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            <span>Architecture & Data Flow Breakdown</span>
          </h2>
          <p className="text-xs text-slate-400">
            How the Vercel-hosted dashboard connects to your local machine:
          </p>
        </div>

        {/* Visual Flow Diagram */}
        <div className="p-6 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto space-y-4">
          <div className="text-center font-semibold text-indigo-300 pb-2 border-b border-slate-800">
            WHERE YOUR DATA GOES
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div className="p-4 rounded-lg bg-slate-800/60 border border-slate-700/60 space-y-2">
              <div className="font-bold text-white text-sm">Vercel Cloud</div>
              <div className="text-[11px] text-indigo-300">Next.js UI Dashboard</div>
              <div className="text-[11px] text-slate-400">Renders interface in your browser. Stores 0% of candidate data.</div>
            </div>

            <div className="flex flex-col items-center justify-center py-2 text-emerald-400">
              <span className="text-[11px] font-bold">Localhost HTTP (127.0.0.1:8000)</span>
              <span className="text-slate-500">⇄ Strict Browser Fetch ⇄</span>
              <span className="text-[10px] text-slate-400">CORS Whitelisted Origin Only</span>
            </div>

            <div className="p-4 rounded-lg bg-emerald-950/40 border border-emerald-700/60 space-y-2">
              <div className="font-bold text-white text-sm">Your Local Computer</div>
              <div className="text-[11px] text-emerald-300">CareerCrew Local Agent</div>
              <div className="text-[11px] text-slate-300">Ollama + CrewAI + SQLite + ChromaDB + Git</div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-[11px]">
            <div className="p-2 bg-slate-800/40 rounded border border-slate-700/40">
              <span className="text-slate-400 block">Resume Files:</span>
              <span className="font-bold text-emerald-400">Local Disk</span>
            </div>
            <div className="p-2 bg-slate-800/40 rounded border border-slate-700/40">
              <span className="text-slate-400 block">Git Repositories:</span>
              <span className="font-bold text-emerald-400">Local Disk</span>
            </div>
            <div className="p-2 bg-slate-800/40 rounded border border-slate-700/40">
              <span className="text-slate-400 block">AI Reasoning:</span>
              <span className="font-bold text-emerald-400">Local Ollama</span>
            </div>
            <div className="p-2 bg-slate-800/40 rounded border border-slate-700/40">
              <span className="text-slate-400 block">Cloud AI APIs:</span>
              <span className="font-bold text-red-400">NONE</span>
            </div>
          </div>
        </div>
      </div>

      {/* Data Artifacts Table */}
      <div className="border border-surface-border rounded-xl bg-surface overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-400" />
            <h2 className="font-semibold text-white text-base">Data Processing Matrix</h2>
          </div>
          <span className="text-xs text-emerald-400 font-mono">
            8/8 Subsystems Local-Only
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900/60 text-xs text-slate-400 uppercase font-mono tracking-wider">
              <tr>
                <th className="px-6 py-3">Data Artifact</th>
                <th className="px-6 py-3">Storage Location</th>
                <th className="px-6 py-3">Processing Engine</th>
                <th className="px-6 py-3">Cloud / Vercel Exposure</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border text-xs">
              {dataArtifacts.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/20 transition-colors">
                  <td className="px-6 py-4 font-medium text-white">
                    {item.name}
                  </td>
                  <td className="px-6 py-4 font-mono text-slate-300">
                    {item.storage}
                  </td>
                  <td className="px-6 py-4 text-slate-300">
                    {item.processing}
                  </td>
                  <td className="px-6 py-4 font-semibold text-emerald-400 font-mono">
                    {item.cloudExposure}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Technical Guarantees Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="border border-surface-border rounded-xl bg-surface p-6 space-y-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-white text-sm">Localhost Binding</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            The CareerCrew Local Agent binds exclusively to <code className="text-slate-300">127.0.0.1</code>, refusing external network interfaces or public exposure.
          </p>
        </div>

        <div className="border border-surface-border rounded-xl bg-surface p-6 space-y-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-600/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <EyeOff className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-white text-sm">Strict CORS Restrictions</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Wildcard <code className="text-slate-300">*</code> CORS is strictly rejected by the server configuration validator. Only authenticated dashboard origins are allowed.
          </p>
        </div>

        <div className="border border-surface-border rounded-xl bg-surface p-6 space-y-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
            <GitBranch className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-white text-sm">Read-Only Git Scanning</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            The project intelligence engine operates in strict read-only inspection mode. It cannot push, commit, delete, or modify your repositories.
          </p>
        </div>
      </div>

      {/* Honest Disclaimer */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 leading-relaxed">
        <strong className="text-slate-300 block mb-1">Architecture Disclosure & Scope:</strong>
        CareerCrew technical privacy guarantees are enforced by running the API, AI models, vector database, and Git analyzers exclusively on your local machine.
        When accessing CareerCrew via a hosted Vercel deployment, your browser communicates with your Local Agent over <code className="text-slate-300">http://127.0.0.1:8000</code>.
        No resume text, code lines, or analysis dossiers are ever dispatched to Vercel servers or external cloud LLM providers.
      </div>
    </div>
  );
}
