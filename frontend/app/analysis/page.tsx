"use client";

import { useState } from "react";
import {
  Sparkles,
  UploadCloud,
  FileText,
  Briefcase,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Layers,
  Cpu,
  Clock,
  ShieldCheck,
  ChevronRight,
  Filter,
  RefreshCw,
  FolderGit2,
  FileCode,
  ArrowRight,
  Zap,
  Users,
  Scale,
  Bot,
} from "lucide-react";

import {
  analyzeMatch,
  fetchAnalysisEvidence,
  runCrewAnalysis,
  runBenchmarkAnalysis,
} from "@/lib/api";
import {
  AnalysisResult,
  RequirementMatchResult,
  EvidenceAssessment,
  FinalAnalysisDossier,
  BenchmarkComparisonResult,
} from "@/types";


const SAMPLE_RESUME = `Alex Chen
alex.chen@example.com | (555) 321-9876 | github.com/alexchen-dev
Location: San Francisco, CA

Professional Summary:
Senior Backend Engineer with 5+ years of experience designing high-throughput distributed microservices in Python, FastAPI, and PostgreSQL. Experienced with Docker, Redis caching, CI/CD pipelines, and AWS cloud deployments.

Skills:
- Programming Languages: Python, JavaScript, TypeScript, SQL, Bash
- Frameworks & Libraries: FastAPI, Flask, Pydantic, SQLAlchemy, PyTest
- Databases: PostgreSQL, SQLite, Redis, MongoDB
- Cloud & DevOps: Docker, Kubernetes, AWS (EC2, S3, RDS), Git, Linux, GitHub Actions
- Architecture: Microservices, REST APIs, Event-Driven Architecture, Distributed Systems

Work Experience:
Senior Software Engineer | CloudScale Systems | 2021 - Present
- Designed and maintained core transaction microservices using Python and FastAPI handling 15k req/sec.
- Optimized relational database schemas and indexed PostgreSQL queries, reducing latency by 42%.
- Automated CI/CD container deployments to AWS via Docker and GitHub Actions.

Software Engineer | NextGen Apps | 2018 - 2021
- Built RESTful web APIs with Python and Flask. Integrated Redis caching to reduce database read load.
- Implemented unit and integration test suites using PyTest, achieving 88% test coverage.

Education:
Bachelor of Science in Computer Science | University of California, Berkeley | 2014 - 2018

Projects:
Distributed Task Queue:
- Open-source asynchronous task broker built with Python, FastAPI, and Redis with real-time telemetry.
Real-Time Analytics Pipeline:
- High-performance data ingestion service using PostgreSQL and Docker containers.`;

const SAMPLE_JD = `Senior Backend Engineer (Python / Distributed Systems)
Company: DataSphere Innovations
Location: Remote / Hybrid

About the Role:
We are looking for a Senior Backend Engineer to join our core infrastructure crew. You will design resilient, scalable backend services and distributed data pipelines.

Requirements:
- 5+ years of software engineering experience in backend development.
- Strong proficiency in Python and modern backend frameworks (FastAPI or Flask).
- Deep experience with relational databases (PostgreSQL preferred) and SQL query optimization.
- Proven experience architecting microservices and distributed systems.
- Bachelor's degree in Computer Science or equivalent practical experience.

Preferred Qualifications:
- Experience with Docker and container orchestration (Kubernetes).
- Familiarity with cloud platforms (AWS, GCP).
- Experience with in-memory caching solutions such as Redis.
- Solid understanding of CI/CD pipelines and automated testing with PyTest.`;

export default function AnalysisPage() {
  const [inputMode, setInputMode] = useState<"text" | "file">("text");
  const [resumeText, setResumeText] = useState<string>("");
  const [jdText, setJdText] = useState<string>("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);

  const [loading, setLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [evidenceAssessment, setEvidenceAssessment] = useState<EvidenceAssessment | null>(null);
  const [loadingEvidence, setLoadingEvidence] = useState<boolean>(false);

  const [filterStatus, setFilterStatus] = useState<"all" | "match" | "partial_match" | "missing">("all");
  const [filterType, setFilterType] = useState<"all" | "required" | "preferred">("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [dossier, setDossier] = useState<FinalAnalysisDossier | null>(null);
  const [benchmarkResult, setBenchmarkResult] = useState<BenchmarkComparisonResult | null>(null);
  const [activeAnalysisMode, setActiveAnalysisMode] = useState<"baseline" | "crew" | "benchmark">("baseline");

  const handleLoadSample = () => {
    setInputMode("text");
    setResumeText(SAMPLE_RESUME);
    setJdText(SAMPLE_JD);
    setError(null);
  };

  const handleClear = () => {
    setResumeText("");
    setJdText("");
    setResumeFile(null);
    setJdFile(null);
    setError(null);
    setResult(null);
    setEvidenceAssessment(null);
    setDossier(null);
    setBenchmarkResult(null);
    setActiveAnalysisMode("baseline");
  };

  const handleRunCrewAnalysis = async () => {
    setError(null);
    if (!resumeText.trim() || !jdText.trim()) {
      setError("Please provide both Resume text and Job Description text for multi-agent analysis.");
      return;
    }
    setLoading(true);
    setStatusMessage("Orchestrating 5 CrewAI agents (Manager, JD, Resume, Evidence, Match)...");
    try {
      const data = await runCrewAnalysis({
        raw_resume_text: resumeText,
        raw_jd_text: jdText,
        use_live_llm: true,
      });
      setDossier(data);
      setActiveAnalysisMode("crew");
    } catch (err: any) {
      setError(err?.message || "Failed to execute multi-agent analysis.");
    } finally {
      setLoading(false);
      setStatusMessage("");
    }
  };

  const handleRunBenchmark = async () => {
    setError(null);
    if (!resumeText.trim() || !jdText.trim()) {
      setError("Please provide both Resume text and Job Description text for benchmark comparison.");
      return;
    }
    setLoading(true);
    setStatusMessage("Executing side-by-side benchmark (Baseline vs CrewAI Multi-Agent)...");
    try {
      const bData = await runBenchmarkAnalysis({
        raw_resume_text: resumeText,
        raw_jd_text: jdText,
      });
      setBenchmarkResult(bData);
      setActiveAnalysisMode("benchmark");
    } catch (err: any) {
      setError(err?.message || "Failed to execute benchmark analysis.");
    } finally {
      setLoading(false);
      setStatusMessage("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setActiveAnalysisMode("baseline");

    if (inputMode === "text" && (!resumeText.trim() || !jdText.trim())) {
      setError("Please provide both Resume text and Job Description text.");
      return;
    }
    if (inputMode === "file" && (!resumeFile || !jdFile)) {
      setError("Please select both a Resume document and a Job Description document.");
      return;
    }

    setLoading(true);
    setStatusMessage("Extracting structured profiles with local Llama 3.2:3b...");

    try {
      const formData = new FormData();
      if (inputMode === "file") {
        if (resumeFile) formData.append("resume_file", resumeFile);
        if (jdFile) formData.append("jd_file", jdFile);
      } else {
        formData.append("resume_text", resumeText);
        formData.append("jd_text", jdText);
      }

      setStatusMessage("Computing embedding similarities and scoring dimensions...");
      const data: AnalysisResult = await analyzeMatch(formData);
      setResult(data);

      if (data.analysis_run_id) {
        try {
          setStatusMessage("Correlating local repository evidence against claims...");
          setLoadingEvidence(true);
          const evData = await fetchAnalysisEvidence(data.analysis_run_id);
          setEvidenceAssessment(evData);
        } catch (evErr) {
          console.warn("Evidence correlation skipped:", evErr);
        } finally {
          setLoadingEvidence(false);
        }
      }

    } catch (err: any) {
      setError(err?.message || "Failed to analyze match. Ensure the local backend and Ollama are running.");
    } finally {
      setLoading(false);
      setStatusMessage("");
    }
  };

  const filteredRequirements = (result?.requirements_analysis || []).filter((req: RequirementMatchResult) => {
    if (filterStatus !== "all" && req.status !== filterStatus) return false;
    if (filterType !== "all" && req.requirement_type !== filterType) return false;
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const matchSkill = req.canonical_skill.toLowerCase().includes(query);
      const matchText = req.original_text.toLowerCase().includes(query);
      const matchExpl = req.explanation.toLowerCase().includes(query);
      if (!matchSkill && !matchText && !matchExpl) return false;
    }
    return true;
  });

  const getScoreColor = (score: number) => {
    if (score >= 75) return "text-emerald-400";
    if (score >= 50) return "text-amber-400";
    return "text-rose-400";
  };

  const getScoreBg = (score: number) => {
    if (score >= 75) return "bg-emerald-500/10 border-emerald-500/30 text-emerald-300";
    if (score >= 50) return "bg-amber-500/10 border-amber-500/30 text-amber-300";
    return "bg-rose-500/10 border-rose-500/30 text-rose-300";
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Page Title & Context Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">
              Explainable Match Analysis Engine
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Phase 2 intelligence layer transforming resumes and job descriptions into structured profiles.
            Evaluates candidate coverage across 7 weighted dimensions using local Llama 3.2:3b and nomic-embed-text.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>100% Local Inference</span>
          </div>
          <div className="px-3 py-1.5 rounded-full bg-slate-800 text-slate-300 text-xs font-mono border border-slate-700">
            Phase 2 Verified
          </div>
        </div>
      </div>

      {/* Input Configuration & Action Bar */}
      <div className="p-6 rounded-2xl bg-surface border border-surface-border space-y-6 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-surface-border pb-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Input Mode:
            </span>
            <div className="inline-flex rounded-lg bg-slate-900 p-1 border border-slate-800">
              <button
                type="button"
                onClick={() => setInputMode("text")}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  inputMode === "text"
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Pasted Text
              </button>
              <button
                type="button"
                onClick={() => setInputMode("file")}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  inputMode === "file"
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                File Upload (PDF/DOCX)
              </button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleLoadSample}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-medium transition-colors"
            >
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              <span>Load Python Sample</span>
            </button>
            {(resumeText || jdText || resumeFile || jdFile || result) && (
              <button
                type="button"
                onClick={handleClear}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 text-xs font-medium transition-colors"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Resume Input Panel */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-semibold text-white flex items-center gap-2">
                  <FileText className="w-4 h-4 text-indigo-400" />
                  Candidate Resume
                </label>
                {inputMode === "text" && (
                  <span className="text-[11px] font-mono text-slate-400">
                    {resumeText.length} chars
                  </span>
                )}
              </div>

              {inputMode === "text" ? (
                <textarea
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  placeholder="Paste candidate resume text here (Markdown, Plain text, formatted sections)..."
                  rows={12}
                  className="w-full p-3.5 rounded-xl bg-slate-900 border border-surface-border text-slate-200 text-xs font-mono placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/80 transition-colors resize-y leading-relaxed"
                />
              ) : (
                <div className="p-8 border-2 border-dashed border-surface-border rounded-xl text-center bg-slate-900/50 hover:bg-slate-900 transition-colors">
                  <UploadCloud className="w-8 h-8 text-indigo-400 mx-auto mb-2" />
                  <p className="text-xs font-medium text-slate-300 mb-1">
                    {resumeFile ? resumeFile.name : "Select or drop resume document"}
                  </p>
                  <p className="text-[11px] text-slate-500 mb-3">
                    Supports PDF, DOCX, TXT, MD (Max 10MB)
                  </p>
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt,.md"
                    onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                    className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer"
                  />
                </div>
              )}
            </div>

            {/* Job Description Input Panel */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm font-semibold text-white flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-indigo-400" />
                  Target Job Description
                </label>
                {inputMode === "text" && (
                  <span className="text-[11px] font-mono text-slate-400">
                    {jdText.length} chars
                  </span>
                )}
              </div>

              {inputMode === "text" ? (
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste target job posting here with requirements, qualifications, and role responsibilities..."
                  rows={12}
                  className="w-full p-3.5 rounded-xl bg-slate-900 border border-surface-border text-slate-200 text-xs font-mono placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/80 transition-colors resize-y leading-relaxed"
                />
              ) : (
                <div className="p-8 border-2 border-dashed border-surface-border rounded-xl text-center bg-slate-900/50 hover:bg-slate-900 transition-colors">
                  <UploadCloud className="w-8 h-8 text-indigo-400 mx-auto mb-2" />
                  <p className="text-xs font-medium text-slate-300 mb-1">
                    {jdFile ? jdFile.name : "Select or drop job description document"}
                  </p>
                  <p className="text-[11px] text-slate-500 mb-3">
                    Supports PDF, DOCX, TXT, MD (Max 10MB)
                  </p>
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt,.md"
                    onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                    className="text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer"
                  />
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex flex-col lg:flex-row items-center justify-between gap-4 pt-2">
            <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>Ollama llama3.2:3b &bull; nomic-embed-text</span>
            </div>

            <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 sm:flex-none px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 hover:text-white font-medium text-xs transition-all border border-slate-700 flex items-center justify-center gap-2 cursor-pointer"
              >
                {loading && activeAnalysisMode === "baseline" ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                )}
                <span>A. Baseline Match (Phase 2)</span>
              </button>

              <button
                type="button"
                onClick={handleRunCrewAnalysis}
                disabled={loading}
                className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs transition-all shadow-lg shadow-indigo-600/20 flex items-center justify-center gap-2 cursor-pointer"
              >
                {loading && activeAnalysisMode === "crew" ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Users className="w-3.5 h-3.5 text-indigo-200" />
                )}
                <span>B. CrewAI Multi-Agent (Phase 4)</span>
              </button>

              <button
                type="button"
                onClick={handleRunBenchmark}
                disabled={loading}
                className="flex-1 sm:flex-none px-4 py-2.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 disabled:opacity-50 text-emerald-300 font-medium text-xs transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                {loading && activeAnalysisMode === "benchmark" ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Scale className="w-3.5 h-3.5 text-emerald-400" />
                )}
                <span>Compare &amp; Benchmark</span>
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Multi-Agent CrewAI Dossier & Telemetry View */}
      {dossier && activeAnalysisMode === "crew" && (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Multi-Agent Header Banner */}
          <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-br from-surface to-slate-900 border border-indigo-500/40 shadow-2xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-surface-border">
              <div className="flex items-center gap-5">
                <div className="relative w-24 h-24 rounded-2xl bg-slate-950 border border-indigo-500/30 flex flex-col items-center justify-center shrink-0 shadow-inner">
                  <span className={`text-3xl font-extrabold tracking-tight ${getScoreColor(dossier.overall_match_score)}`}>
                    {dossier.overall_match_score}%
                  </span>
                  <span className="text-[10px] uppercase font-mono text-slate-500 tracking-wider">
                    Orchestrated
                  </span>
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-xs font-mono font-semibold">
                      Mode: CrewAI Multi-Agent
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-semibold">
                      {dossier.classification}
                    </span>
                  </div>
                  <h2 className="text-xl font-bold text-white">Synthesized Candidate Analysis Dossier</h2>
                  <p className="text-xs text-slate-400">
                    5 Autonomous CrewAI agents coordinated by Manager Agent &bull; Zero Hallucination Guardrails
                  </p>
                </div>
              </div>

              {/* Evidence Confidence Counter */}
              <div className="flex items-center gap-4 bg-slate-950/60 p-4 rounded-xl border border-surface-border">
                <ShieldCheck className="w-8 h-8 text-emerald-400 shrink-0" />
                <div>
                  <div className="text-lg font-bold text-white">
                    {dossier.evidence_confidence_score}%
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono">
                    Evidence Confidence ({dossier.verified_skills.length} verified)
                  </div>
                </div>
              </div>
            </div>

            {/* Strengths & Gaps Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-6">
              <div className="p-4 rounded-xl bg-slate-950/40 border border-emerald-500/20 space-y-2">
                <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Key Strengths &amp; Verified Competencies
                </h4>
                <ul className="space-y-1.5">
                  {dossier.key_strengths.map((str, idx) => (
                    <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                      <span className="text-emerald-400">&bull;</span>
                      <span>{str}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 rounded-xl bg-slate-950/40 border border-amber-500/20 space-y-2">
                <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5" />
                  Identified Gaps &amp; Missing Requirements
                </h4>
                <ul className="space-y-1.5">
                  {dossier.key_gaps.map((gap, idx) => (
                    <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                      <span className="text-amber-400">&bull;</span>
                      <span>{gap}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Agent Execution Telemetry Panel */}
          {dossier.agent_execution_summary && (
            <div className="p-6 rounded-2xl bg-surface border border-surface-border space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-surface-border">
                <div className="flex items-center gap-2">
                  <Bot className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-sm font-bold text-white">Agent Execution Telemetry</h3>
                </div>
                <div className="text-xs font-mono text-slate-400">
                  Total: {dossier.agent_execution_summary.total_duration_ms} ms &bull; {dossier.agent_execution_summary.total_llm_invocations} LLM &bull; {dossier.agent_execution_summary.total_tool_invocations} Tools
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                {dossier.agent_execution_summary.telemetry.map((t, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-200">{t.agent_name}</span>
                      <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 font-mono">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                        {t.status}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 truncate">{t.task_name}</p>
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-1 border-t border-slate-800/80">
                      <span>{t.duration_ms} ms</span>
                      <span>{t.tool_invocations} tools</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-2 flex flex-wrap items-center gap-2 text-xs">
                <span className="text-slate-500 font-mono">Phase 5 Inactive Agents:</span>
                {dossier.agent_execution_summary.agents_inactive.map((name, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-slate-800/60 border border-slate-700/50 text-[11px] font-mono text-slate-400">
                    {name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Comparative Benchmark View */}
      {benchmarkResult && activeAnalysisMode === "benchmark" && (
        <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-br from-surface to-slate-900 border border-emerald-500/40 shadow-2xl space-y-6 animate-in fade-in duration-300">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
            <div className="flex items-center gap-3">
              <Scale className="w-6 h-6 text-emerald-400" />
              <div>
                <h2 className="text-lg font-bold text-white">Comparative Benchmark: Baseline vs Multi-Agent</h2>
                <p className="text-xs text-slate-400 font-mono">Contrasting deterministic Phase 2 vs CrewAI orchestration</p>
              </div>
            </div>
            <div className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs">
              Score Delta: {benchmarkResult.score_differential >= 0 ? `+${benchmarkResult.score_differential}` : benchmarkResult.score_differential}%
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Baseline Card */}
            <div className="p-5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">A. Deterministic Baseline</span>
                <span className="text-2xl font-extrabold text-indigo-400 font-mono">{benchmarkResult.baseline_match_score}%</span>
              </div>
              <div className="space-y-1.5 text-xs text-slate-400 font-mono">
                <div className="flex justify-between">
                  <span>Execution Time:</span>
                  <span className="text-slate-200">{benchmarkResult.baseline_execution_ms} ms</span>
                </div>
                <div className="flex justify-between">
                  <span>LLM Invocations:</span>
                  <span className="text-slate-200">{benchmarkResult.baseline_llm_calls}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tool Calls:</span>
                  <span className="text-slate-200">{benchmarkResult.baseline_tool_calls}</span>
                </div>
                <div className="flex justify-between">
                  <span>Missing Gaps:</span>
                  <span className="text-slate-200">{benchmarkResult.baseline_missing_requirements_count}</span>
                </div>
              </div>
            </div>

            {/* CrewAI Card */}
            <div className="p-5 rounded-xl bg-slate-950/60 border border-indigo-500/30 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-indigo-300 uppercase tracking-wider">B. CrewAI Multi-Agent</span>
                <span className="text-2xl font-extrabold text-emerald-400 font-mono">{benchmarkResult.crew_match_score}%</span>
              </div>
              <div className="space-y-1.5 text-xs text-slate-400 font-mono">
                <div className="flex justify-between">
                  <span>Execution Time:</span>
                  <span className="text-slate-200">{benchmarkResult.crew_execution_ms} ms</span>
                </div>
                <div className="flex justify-between">
                  <span>LLM Invocations:</span>
                  <span className="text-slate-200">{benchmarkResult.crew_llm_calls}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tool Calls:</span>
                  <span className="text-slate-200">{benchmarkResult.crew_tool_calls}</span>
                </div>
                <div className="flex justify-between">
                  <span>Missing Gaps:</span>
                  <span className="text-slate-200">{benchmarkResult.crew_missing_requirements_count}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Insights List */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-surface-border space-y-2">
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Benchmark Synthesis Insights</h4>
            <ul className="space-y-1">
              {benchmarkResult.synthesis_insights.map((insight, idx) => (
                <li key={idx} className="text-xs text-slate-300 flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Analysis Output Section */}
      {result && (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Hero Overview Card */}
          <div className="p-6 md:p-8 rounded-2xl bg-gradient-to-br from-surface to-slate-900 border border-surface-border shadow-2xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-surface-border">
              <div className="flex items-center gap-5">
                {/* Match Score Radial Display */}
                <div className="relative w-24 h-24 rounded-2xl bg-slate-950 border border-surface-border flex flex-col items-center justify-center shrink-0 shadow-inner">
                  <span className={`text-3xl font-extrabold tracking-tight ${getScoreColor(result.overall_score)}`}>
                    {result.overall_score}%
                  </span>
                  <span className="text-[10px] uppercase font-mono text-slate-500 tracking-wider">
                    Match
                  </span>
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${getScoreBg(result.overall_score)}`}>
                      {result.match_classification || (result.overall_score >= 75 ? "Strong Match" : result.overall_score >= 50 ? "Moderate Match" : "Poor Match")}
                    </span>
                    {result.analysis_run_id && (
                      <span className="text-[11px] font-mono text-slate-500">
                        Run: {result.analysis_run_id.slice(0, 8)}
                      </span>
                    )}
                  </div>
                  <h2 className="text-xl font-bold text-white tracking-tight">
                    Candidate Compatibility Score
                  </h2>
                  <p className="text-xs text-slate-400 max-w-xl leading-relaxed">
                    {result.summary || result.summary_explanation}
                  </p>
                </div>
              </div>

              {/* Requirement Counts Quick Stat */}
              <div className="grid grid-cols-3 gap-3 self-stretch md:self-auto shrink-0 text-center">
                <div className="p-3 rounded-xl bg-slate-950/60 border border-emerald-500/20">
                  <div className="text-lg font-bold text-emerald-400">
                    {result.matched_requirements.length}
                  </div>
                  <div className="text-[10px] uppercase font-mono text-slate-400">
                    Matches
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950/60 border border-amber-500/20">
                  <div className="text-lg font-bold text-amber-400">
                    {(result.partial_matches || result.partial_requirements || []).length}
                  </div>
                  <div className="text-[10px] uppercase font-mono text-slate-400">
                    Partial
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-950/60 border border-rose-500/20">
                  <div className="text-lg font-bold text-rose-400">
                    {result.missing_requirements.length}
                  </div>
                  <div className="text-[10px] uppercase font-mono text-slate-400">
                    Missing
                  </div>
                </div>
              </div>
            </div>

            {/* Local AI Execution Telemetry Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-4 text-xs font-mono text-slate-400">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                  <span>LLM: {result.metadata.model_name}</span>
                </div>
                <span className="text-slate-700">&bull;</span>
                <div className="flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Embed: {result.metadata.embedding_model}</span>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-slate-500" />
                  <span>Inference: {Math.round(result.metadata.inference_time_ms)}ms</span>
                </div>
                <span className="text-slate-700">&bull;</span>
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-slate-500" />
                  <span>Total: {Math.round(result.metadata.total_time_ms)}ms</span>
                </div>
              </div>
            </div>
          </div>

          {/* 7 Weighted Dimension Score Cards */}
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Multidimensional Scoring Breakdown
              </h3>
              <p className="text-xs text-slate-400">
                Transparent multi-factor assessment calculated using deterministic weights bounded [0.0 - 100.0]
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Dimension 1: Required Skills */}
              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300">Required Skills</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    35% Weight
                  </span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className={`text-xl font-bold ${getScoreColor(result.dimension_scores.required_skill_score)}`}>
                    {result.dimension_scores.required_skill_score}%
                  </span>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${result.dimension_scores.required_skill_score}%` }}
                  />
                </div>
              </div>

              {/* Dimension 2: Preferred Skills */}
              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300">Preferred Skills</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    15% Weight
                  </span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className={`text-xl font-bold ${getScoreColor(result.dimension_scores.preferred_skill_score)}`}>
                    {result.dimension_scores.preferred_skill_score}%
                  </span>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${result.dimension_scores.preferred_skill_score}%` }}
                  />
                </div>
              </div>

              {/* Dimension 3: Technical Depth */}
              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300">Technical Depth</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    15% Weight
                  </span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className={`text-xl font-bold ${getScoreColor(result.dimension_scores.technical_depth_score)}`}>
                    {result.dimension_scores.technical_depth_score}%
                  </span>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${result.dimension_scores.technical_depth_score}%` }}
                  />
                </div>
              </div>

              {/* Dimension 4: Project Relevance */}
              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300">Project Relevance</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    15% Weight
                  </span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className={`text-xl font-bold ${getScoreColor(result.dimension_scores.project_relevance_score)}`}>
                    {result.dimension_scores.project_relevance_score}%
                  </span>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${result.dimension_scores.project_relevance_score}%` }}
                  />
                </div>
              </div>

              {/* Dimension 5: Experience Match */}
              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300">Experience Match</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    10% Weight
                  </span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className={`text-xl font-bold ${getScoreColor(result.dimension_scores.experience_alignment_score ?? result.dimension_scores.experience_score ?? 0)}`}>
                    {result.dimension_scores.experience_alignment_score ?? result.dimension_scores.experience_score ?? 0}%
                  </span>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${result.dimension_scores.experience_alignment_score ?? result.dimension_scores.experience_score ?? 0}%` }}
                  />
                </div>
              </div>

              {/* Dimension 6: Education Alignment */}
              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300">Education Alignment</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    5% Weight
                  </span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className={`text-xl font-bold ${getScoreColor(result.dimension_scores.education_alignment_score ?? result.dimension_scores.education_score ?? 0)}`}>
                    {result.dimension_scores.education_alignment_score ?? result.dimension_scores.education_score ?? 0}%
                  </span>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${result.dimension_scores.education_alignment_score ?? result.dimension_scores.education_score ?? 0}%` }}
                  />
                </div>
              </div>

              {/* Dimension 7: Keyword Overlap */}
              <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-2 sm:col-span-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300">Keyword Coverage</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                    5% Weight
                  </span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className={`text-xl font-bold ${getScoreColor(result.dimension_scores.keyword_coverage_score ?? result.dimension_scores.keyword_score ?? 0)}`}>
                    {result.dimension_scores.keyword_coverage_score ?? result.dimension_scores.keyword_score ?? 0}%
                  </span>
                </div>
                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${result.dimension_scores.keyword_coverage_score ?? result.dimension_scores.keyword_score ?? 0}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Evaluated Project Semantic Relevance */}
          {result.project_relevance && result.project_relevance.length > 0 && (
            <div className="p-6 rounded-2xl bg-surface border border-surface-border space-y-4">
              <div className="flex items-center gap-2">
                <FolderGit2 className="w-4 h-4 text-indigo-400" />
                <h3 className="text-base font-bold text-white tracking-tight">
                  Semantic Project Evidence
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.project_relevance.map((proj, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-surface-border space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sm text-white">{proj.project_name}</span>
                      <span className="px-2 py-0.5 rounded text-xs font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                        {Math.round(proj.similarity_score * 100)}% Sim
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">{proj.overlap_summary}</p>
                    {proj.technologies && proj.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {proj.technologies.map((t, tidx) => (
                          <span key={tidx} className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Phase 3: Evidence Grounding & Verification Card */}
          {evidenceAssessment && (

            <div className="p-6 md:p-8 rounded-2xl bg-surface border border-surface-border space-y-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                      <FolderGit2 className="w-4 h-4" />
                    </span>
                    <h3 className="text-base font-bold text-white tracking-tight">
                      Repository Evidence Verification (Phase 3)
                    </h3>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Direct validation of technical claims against registered local software repositories and commit history.
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-full text-xs font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                    {evidenceAssessment.scanned_projects_count} Repositories Scanned
                  </span>
                </div>
              </div>

              {/* Dual Score Comparison & Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/60 border border-surface-border space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-400">Baseline Match Score</span>
                  <div className="text-2xl font-extrabold text-indigo-400">
                    {result.overall_score}%
                  </div>
                  <p className="text-[11px] text-slate-500">Phase 2 resume-to-JD semantic score</p>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-emerald-500/20 space-y-1">
                  <span className="text-[10px] font-mono uppercase text-emerald-400">Evidence Confidence Score</span>
                  <div className="text-2xl font-extrabold text-emerald-400">
                    {evidenceAssessment.evidence_confidence_score}%
                  </div>
                  <p className="text-[11px] text-slate-500">Backed by genuine local repository proof</p>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-surface-border space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-400">Grounded Skills</span>
                  <div className="text-2xl font-extrabold text-white">
                    {evidenceAssessment.verified_skills_count + evidenceAssessment.likely_skills_count}
                    <span className="text-xs font-normal text-slate-500 ml-1">
                      / {evidenceAssessment.chain.length}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    {evidenceAssessment.verified_skills_count} verified &bull; {evidenceAssessment.likely_skills_count} likely
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-surface-border space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-400">Evidence Coverage</span>
                  <div className="text-2xl font-extrabold text-sky-400">
                    {evidenceAssessment.evidence_coverage_percentage}%
                  </div>
                  <p className="text-[11px] text-slate-500">Requirements verified in repos</p>
                </div>
              </div>

              {/* 4-Part Evidence Chain */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold uppercase text-slate-300 tracking-wider">
                  Requirement Evidence Verification Chain
                </h4>
                <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                  {evidenceAssessment.chain.map((item, cIdx) => (
                    <div
                      key={cIdx}
                      className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 text-xs"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-white">{item.requirement}</span>
                          <span className="text-[10px] font-mono text-slate-500">({item.canonical_skill})</span>
                        </div>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider shrink-0 ${
                            item.verification_status === "VERIFIED"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                              : item.verification_status === "LIKELY"
                              ? "bg-sky-500/10 text-sky-400 border border-sky-500/30"
                              : item.verification_status === "WEAK"
                              ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                              : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                          }`}
                        >
                          {item.verification_status} ({Math.round(item.verification_confidence * 100)}%)
                        </span>
                      </div>

                      {/* 4-Stage Trace */}
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] pt-1 border-t border-slate-800/80">
                        <div>
                          <span className="text-slate-500 block text-[10px] uppercase font-mono">Resume Claim</span>
                          <span className={item.resume_claimed ? "text-emerald-300 font-medium" : "text-slate-400"}>
                            {item.resume_claimed ? "✓ Claimed on Resume" : "— Not Mentioned"}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block text-[10px] uppercase font-mono">Supporting Projects</span>
                          <span className="text-slate-300">
                            {item.projects_found && item.projects_found.length > 0
                              ? item.projects_found.join(", ")
                              : "None found"}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 block text-[10px] uppercase font-mono">Grounding Rationale</span>
                          <span className="text-slate-400">{item.rationale}</span>
                        </div>
                      </div>

                      {/* Code/File Evidence Snippet */}
                      {item.repository_evidence && item.repository_evidence.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-800/60 flex flex-wrap gap-2 text-[10px] font-mono">
                          {item.repository_evidence.map((ev, eIdx) => (
                            <span key={eIdx} className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-indigo-300 flex items-center gap-1">
                              <FileCode className="w-3 h-3 text-slate-500" />
                              {ev.source_file} ({ev.evidence_type})
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Detailed Requirement Match Deep-Dive */}

          <div className="p-6 md:p-8 rounded-2xl bg-surface border border-surface-border space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-border pb-4">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">
                  Requirement Verification & Gap Identification
                </h3>
                <p className="text-xs text-slate-400">
                  Detailed inspection of job requirements mapped to grounded resume evidence
                </p>
              </div>

              {/* Status and Type Filter Controls */}
              <div className="flex flex-wrap items-center gap-2">
                {/* Status Tabs */}
                <div className="inline-flex rounded-lg bg-slate-900 p-1 border border-slate-800 text-xs font-medium">
                  <button
                    onClick={() => setFilterStatus("all")}
                    className={`px-2.5 py-1 rounded transition-colors ${
                      filterStatus === "all" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                    }`}
                  >
                    All ({result.requirements_analysis.length})
                  </button>
                  <button
                    onClick={() => setFilterStatus("match")}
                    className={`px-2.5 py-1 rounded transition-colors ${
                      filterStatus === "match" ? "bg-emerald-600 text-white" : "text-emerald-400 hover:text-white"
                    }`}
                  >
                    Matches ({result.matched_requirements.length})
                  </button>
                  <button
                    onClick={() => setFilterStatus("partial_match")}
                    className={`px-2.5 py-1 rounded transition-colors ${
                      filterStatus === "partial_match" ? "bg-amber-600 text-white" : "text-amber-400 hover:text-white"
                    }`}
                  >
                    Partial ({(result.partial_matches || result.partial_requirements || []).length})
                  </button>
                  <button
                    onClick={() => setFilterStatus("missing")}
                    className={`px-2.5 py-1 rounded transition-colors ${
                      filterStatus === "missing" ? "bg-rose-600 text-white" : "text-rose-400 hover:text-white"
                    }`}
                  >
                    Missing ({result.missing_requirements.length})
                  </button>
                </div>
              </div>
            </div>

            {/* Filter Search Input */}
            <div className="flex items-center gap-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search requirements by skill (e.g., Python, Docker, PostgreSQL)..."
                className="flex-1 p-2.5 rounded-xl bg-slate-900 border border-surface-border text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
              />
              <div className="inline-flex rounded-lg bg-slate-900 p-1 border border-slate-800 text-xs">
                <button
                  onClick={() => setFilterType("all")}
                  className={`px-2.5 py-1 rounded transition-colors ${
                    filterType === "all" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                  }`}
                >
                  All Types
                </button>
                <button
                  onClick={() => setFilterType("required")}
                  className={`px-2.5 py-1 rounded transition-colors ${
                    filterType === "required" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                  }`}
                >
                  Required Only
                </button>
                <button
                  onClick={() => setFilterType("preferred")}
                  className={`px-2.5 py-1 rounded transition-colors ${
                    filterType === "preferred" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                  }`}
                >
                  Preferred Only
                </button>
              </div>
            </div>

            {/* Requirements Card List */}
            <div className="space-y-3">
              {filteredRequirements.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-500 border border-dashed border-surface-border rounded-xl">
                  No requirements matched the active filters.
                </div>
              ) : (
                filteredRequirements.map((req, idx) => {
                  const status = req.status || (req.classification as any) || "missing";
                  const isMatch = status === "match";
                  const isPartial = status === "partial_match";
                  const isMissing = status === "missing";
                  const evText = req.evidence || (req.candidate_evidence && req.candidate_evidence.length ? req.candidate_evidence.join(", ") : null);

                  return (
                    <div
                      key={idx}
                      className={`p-4 rounded-xl border transition-colors ${
                        isMatch
                          ? "bg-emerald-500/5 border-emerald-500/20"
                          : isPartial
                          ? "bg-amber-500/5 border-amber-500/20"
                          : "bg-rose-500/5 border-rose-500/20"
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                        <div className="space-y-1.5 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            {isMatch && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
                            {isPartial && <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />}
                            {isMissing && <XCircle className="w-4 h-4 text-rose-400 shrink-0" />}

                            <span className="font-bold text-sm text-white">
                              {req.canonical_skill}
                            </span>

                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium uppercase ${
                                req.requirement_type === "required"
                                  ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                                  : "bg-slate-800 text-slate-400 border border-slate-700"
                              }`}
                            >
                              {req.requirement_type}
                            </span>

                            <span className="text-[10px] font-mono text-slate-500">
                              Confidence: {Math.round(req.confidence * 100)}%
                            </span>
                          </div>

                          <p className="text-xs text-slate-300 font-mono pl-6">
                            &ldquo;{req.original_text}&rdquo;
                          </p>

                          <div className="pl-6 pt-1 space-y-1">
                            <p className="text-xs text-slate-400">
                              <span className="text-slate-500 font-semibold">Evaluation: </span>
                              {req.explanation}
                            </p>
                            {evText && (
                              <p className="text-xs text-indigo-300/90 font-mono">
                                <span className="text-slate-500 font-semibold font-sans">Evidence: </span>
                                {evText}
                              </p>
                            )}
                          </div>
                        </div>

                        <div className="self-end sm:self-start">
                          <span
                            className={`px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wider ${
                              isMatch
                                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                : isPartial
                                ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                                : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                            }`}
                          >
                            {isMatch ? "Match" : isPartial ? "Partial Match" : "Missing Gap"}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
