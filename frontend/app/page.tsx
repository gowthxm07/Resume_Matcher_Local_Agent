"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchSystemStatus, fetchDatabaseSummary, fetchLocalAgentHealth } from "@/lib/api";
import { SystemStatusResponse, DatabaseSummary, AgentHealthResponse } from "@/types";
import SystemStatusBadge from "@/components/SystemStatusBadge";
import EmptyStateCard from "@/components/EmptyStateCard";
import AgentArchitectureGrid from "@/components/AgentArchitectureGrid";
import OllamaPlayground from "@/components/OllamaPlayground";
import {
  FileText,
  Briefcase,
  GitBranch,
  Layers,
  Sparkles,
  ShieldCheck,
  Cpu,
  Lock,
  WifiOff,
  CheckCircle2,
  XCircle,
  ArrowRight,
} from "lucide-react";

export default function DashboardPage() {
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [dbSummary, setDbSummary] = useState<DatabaseSummary | null>(null);
  const [agentHealth, setAgentHealth] = useState<AgentHealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    Promise.allSettled([
      fetchSystemStatus(),
      fetchDatabaseSummary(),
      fetchLocalAgentHealth(),
    ]).then(([statusRes, dbRes, agentRes]) => {
      if (statusRes.status === "fulfilled") setStatus(statusRes.value);
      if (dbRes.status === "fulfilled") setDbSummary(dbRes.value);
      if (agentRes.status === "fulfilled") setAgentHealth(agentRes.value);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-8">
      {/* Hero / Platform Banner */}
      <div className="relative p-8 rounded-2xl bg-gradient-to-br from-surface to-slate-900 border border-surface-border overflow-hidden shadow-2xl">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono mb-4">
            <Lock className="w-3.5 h-3.5 text-indigo-400" />
            <span>Zero Paid APIs &bull; 100% Offline-Capable &bull; Local Hardware Only</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            CAREERCREW
          </h1>
          <p className="text-lg text-indigo-300 font-medium mt-1">
            Privacy-First Local Multi-Agent Job Application Optimizer
          </p>

          <p className="text-sm text-slate-400 mt-4 leading-relaxed">
            Career intelligence engine executing locally on Ollama (Llama 3.2:3b), CrewAI,
            and SQLite. Verifies applicant competencies against genuine project evidence without
            ever sending resumes or personal data to cloud providers.
          </p>

          <div className="flex flex-wrap items-center gap-4 mt-6 pt-6 border-t border-slate-800 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-emerald-400" />
              <span>Ollama Llama 3.2:3b</span>
            </div>
            <span className="text-slate-700">&bull;</span>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>No OpenAI / Anthropic</span>
            </div>
            <span className="text-slate-700">&bull;</span>
            <div className="flex items-center gap-2">
              <WifiOff className="w-4 h-4 text-emerald-400" />
              <span>Air-Gapped Compatible</span>
            </div>
          </div>
        </div>
      </div>

      {/* Local Agent Connection Banner */}
      <section>
        {agentHealth?.status === "ready" ? (
          <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs font-mono">
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              <div>
                <span className="text-white font-bold">LOCAL AGENT CONNECTED</span>
                <span className="text-emerald-400 ml-2">(v{agentHealth.version})</span>
                <span className="text-slate-400 block sm:inline sm:ml-3 font-sans">
                  AI Inference, Git scanning, and SQLite running locally on 127.0.0.1. Zero data leaves your machine.
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Link
                href="/get-started"
                className="px-3 py-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-800/80 text-emerald-200 border border-emerald-700/60 transition-colors"
              >
                Compatibility Diagnostics
              </Link>
              <Link
                href="/privacy"
                className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition-colors"
              >
                Privacy Center
              </Link>
            </div>
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-red-950/30 border border-red-800/60 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-red-400 animate-pulse"></span>
              <div>
                <span className="text-white font-bold font-mono">LOCAL AGENT OFFLINE</span>
                <p className="text-red-200/90 mt-0.5">
                  The CareerCrew Local Agent is not responding at http://127.0.0.1:8000. Start your local agent to enable local AI intelligence.
                </p>
              </div>
            </div>
            <Link
              href="/get-started"
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium flex items-center gap-2 shrink-0 transition-colors"
            >
              <span>Setup Local Agent</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        )}
      </section>

      {/* Real-time Host System Telemetry */}
      <section>
        <SystemStatusBadge status={status} loading={loading} />
      </section>

      {/* Interactive Local LLM Inference Console */}
      <section>
        <OllamaPlayground />
      </section>

      {/* Multi-Agent Crew Architecture Blueprint */}
      <section>
        <AgentArchitectureGrid />
      </section>

      {/* Empty State Cards for Planned Features (Phase 2 Roadmap) */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">
            Platform Capabilities Roadmap
          </h2>
          <p className="text-xs text-slate-400">
            Production foundation established in Phase 1; functional agents activate in Phase 2
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <EmptyStateCard
            title="Resume Ingestion & Analysis"
            description="Decomposes resumes into structured skills, chronological work history, and quantifiable metrics using PyMuPDF and python-docx."
            icon={<FileText className="w-5 h-5" />}
            plannedFeatures={[
              "PyMuPDF multi-page parsing",
              "python-docx table extraction",
              "Resume Analyzer Agent",
              "Skill claim cataloging",
            ]}
          />

          <EmptyStateCard
            title="Job Description Parsing"
            description="Reverse engineers job descriptions to extract hard requirements, implicit expectations, and weighted skill hierarchies."
            icon={<Briefcase className="w-5 h-5" />}
            plannedFeatures={[
              "Role requirement weighting",
              "Tech stack identification",
              "JD Analyzer Agent",
              "Domain jargon mapping",
            ]}
          />

          <EmptyStateCard
            title="Codebase Evidence Scanner"
            description="Connects local git repositories and commit history to provide mathematical proof for claimed technical competencies."
            icon={<GitBranch className="w-5 h-5" />}
            plannedFeatures={[
              "Git tree & commit scanning",
              "Code pattern indexing",
              "Evidence Agent audit",
              "ChromaDB local vectorization",
            ]}
          />

          <EmptyStateCard
            title="Zero-Hallucination Optimizer"
            description="Iterative optimization loop with a Fact Checker guardrail guaranteeing zero fabricated skills or metrics."
            icon={<Sparkles className="w-5 h-5" />}
            plannedFeatures={[
              "Bullet point impact refactor",
              "Strict truth verification",
              "Fact Checker Agent guardrail",
              "Convergence loop tracking",
            ]}
          />

          <EmptyStateCard
            title="ATS Emulation & Scoring"
            description="Simulates enterprise Applicant Tracking Systems (Workday, Taleo, Greenhouse) for parseability and keyword density."
            icon={<Layers className="w-5 h-5" />}
            plannedFeatures={[
              "Section hierarchy validation",
              "Keyword density audit",
              "ATS Validator Agent",
              "Format compliance score",
            ]}
          />

          <EmptyStateCard
            title="Grounded Interview Prep"
            description="Generates technical challenges and STAR behavioral interview scenarios directly linked to the candidate's real project evidence."
            icon={<Sparkles className="w-5 h-5" />}
            plannedFeatures={[
              "STAR behavioral prompts",
              "Architecture deep dives",
              "Interview Agent coaching",
              "Real evidence references",
            ]}
          />
        </div>
      </section>
    </div>
  );
}
