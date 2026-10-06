"use client";

import { useState, useEffect } from "react";
import {
  GitBranch,
  FolderPlus,
  RefreshCw,
  Search,
  CheckCircle2,
  AlertTriangle,
  FileCode,
  Layers,
  Database,
  ExternalLink,
  Code,
  ShieldCheck,
  AlertCircle,
  HelpCircle,
  Terminal,
} from "lucide-react";
import {
  fetchProjects,
  registerProject,
  scanProject,
  fetchProjectEvidence,
  verifySkills,
} from "@/lib/api";
import { ProjectResponse, EvidenceItem, SkillVerificationResult, ConfidenceLevel } from "@/types";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Registration modal state
  const [showModal, setShowModal] = useState(false);
  const [registerTab, setRegisterTab] = useState<"local" | "github">("local");
  const [formName, setFormName] = useState("");
  const [formPath, setFormPath] = useState("");
  const [formDesc, setFormDesc] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  // Scanning state
  const [scanningId, setScanningId] = useState<string | null>(null);

  // Evidence view state
  const [selectedProject, setSelectedProject] = useState<ProjectResponse | null>(null);
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [loadingEvidence, setLoadingEvidence] = useState(false);
  const [evidenceFilter, setEvidenceFilter] = useState<string>("ALL");

  // Quick skill verification tester
  const [skillInput, setSkillInput] = useState("");
  const [verificationResult, setVerificationResult] = useState<SkillVerificationResult | null>(null);
  const [verifying, setVerifying] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchProjects();
      setProjects(data);
      if (data.length > 0 && !selectedProject) {
        handleSelectProject(data[0]);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load projects");
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectProject(proj: ProjectResponse) {
    setSelectedProject(proj);
    try {
      setLoadingEvidence(true);
      const ev = await fetchProjectEvidence(proj.id);
      setEvidenceList(ev);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingEvidence(false);
    }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    if (!formName.trim() || !formPath.trim()) {
      setModalError("Please provide both repository name and absolute local path.");
      return;
    }

    try {
      setSubmitting(true);
      setModalError(null);
      const created = await registerProject(formName.trim(), formPath.trim(), formDesc.trim());
      setShowModal(false);
      setFormName("");
      setFormPath("");
      setFormDesc("");
      await loadProjects();
      handleSelectProject(created);
    } catch (err: any) {
      setModalError(err.message || "Registration failed");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleScan(projectId: string) {
    try {
      setScanningId(projectId);
      const updated = await scanProject(projectId);
      setProjects((prev) => prev.map((p) => (p.id === projectId ? updated : p)));
      if (selectedProject?.id === projectId) {
        handleSelectProject(updated);
      }
    } catch (err: any) {
      alert(`Scan failed: ${err.message}`);
    } finally {
      setScanningId(null);
    }
  }

  async function handleQuickVerify(e: React.FormEvent) {
    e.preventDefault();
    if (!skillInput.trim()) return;

    try {
      setVerifying(true);
      const results = await verifySkills([skillInput.trim()]);
      if (results && results.length > 0) {
        setVerificationResult(results[0]);
      }
    } catch (err: any) {
      alert(`Skill verification failed: ${err.message}`);
    } finally {
      setVerifying(false);
    }
  }

  const filteredEvidence = evidenceList.filter((item) => {
    if (evidenceFilter === "ALL") return true;
    return item.confidence_level === evidenceFilter;
  });

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-indigo-400" />
            Project Evidence & Repository Intelligence
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Ground candidate resume claims in genuine local repositories, commits, and configurations
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-sm"
          >
            <FolderPlus className="w-4 h-4" />
            Register Repository
          </button>
        </div>
      </div>

      {/* Quick Skill Verification Bar */}
      <div className="p-4 rounded-xl bg-surface border border-surface-border shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider">
                Instant Skill Grounding Verification
              </h3>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Verify any technical skill against your registered repositories without executing arbitrary code
            </p>
          </div>
          <form onSubmit={handleQuickVerify} className="flex items-center gap-2 max-w-md w-full">
            <input
              type="text"
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              placeholder="e.g. FastAPI, PostgreSQL, Docker, React"
              className="flex-1 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              disabled={verifying || !skillInput.trim()}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs font-medium border border-slate-700 transition"
            >
              {verifying ? "Checking..." : "Verify Claim"}
            </button>
          </form>
        </div>

        {/* Verification Result Display */}
        {verificationResult && (
          <div className="mt-3 pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-slate-300 font-medium">{verificationResult.skill}</span>
              <span className="text-slate-500 font-mono text-[11px]">({verificationResult.canonical_skill})</span>
              <span
                className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                  verificationResult.status === "VERIFIED"
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                    : verificationResult.status === "LIKELY"
                    ? "bg-sky-500/10 text-sky-400 border border-sky-500/30"
                    : verificationResult.status === "WEAK"
                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                    : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                }`}
              >
                {verificationResult.status} ({Math.round(verificationResult.confidence * 100)}%)
              </span>
            </div>
            <div className="text-[11px] text-slate-400">
              {verificationResult.summary}
            </div>
          </div>
        )}
      </div>

      {/* Main Grid: Projects List & Evidence Details */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">
          <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-indigo-400" />
          Loading registered software repositories...
        </div>
      ) : projects.length === 0 ? (
        <div className="p-12 rounded-xl bg-surface border border-surface-border text-center max-w-lg mx-auto my-8">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-4 border border-indigo-500/20">
            <FolderPlus className="w-6 h-6" />
          </div>
          <h2 className="text-sm font-semibold text-white mb-2">No Local Repositories Registered</h2>
          <p className="text-xs text-slate-400 leading-relaxed mb-6">
            Register your local software projects (e.g. <code className="text-indigo-300">D:\Projects\MyApp</code>).
            CareerCrew scans manifests, configurations, Dockerfiles, and commit histories to verify the skills listed on your resume.
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition"
          >
            Register Your First Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Projects Column (5 cols) */}
          <div className="lg:col-span-5 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400 px-1">
              <span>REGISTERED REPOSITORIES ({projects.length})</span>
            </div>

            <div className="space-y-3">
              {projects.map((proj) => {
                const isSelected = selectedProject?.id === proj.id;
                const isScanning = scanningId === proj.id;

                return (
                  <div
                    key={proj.id}
                    onClick={() => handleSelectProject(proj)}
                    className={`p-4 rounded-xl border transition cursor-pointer ${
                      isSelected
                        ? "bg-slate-800/80 border-indigo-500/60 shadow-md ring-1 ring-indigo-500/30"
                        : "bg-surface border-surface-border hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-xs font-semibold text-white truncate">{proj.name}</h3>
                          {proj.evidence_count > 0 ? (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                              🟢 Verified
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-900 text-slate-400 border border-slate-700">
                              ⚪ Unscanned
                            </span>
                          )}
                          {proj.git_branch && (
                            <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-[10px] text-slate-300 font-mono flex items-center gap-1">
                              <GitBranch className="w-2.5 h-2.5 text-indigo-400" />
                              {proj.git_branch}
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 font-mono truncate mt-1">
                          Repository: {proj.repo_path}
                        </p>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleScan(proj.id);
                        }}
                        disabled={isScanning}
                        title="Re-scan repository for evidence"
                        className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
                      >
                        <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? "animate-spin text-indigo-400" : ""}`} />
                      </button>
                    </div>

                    {/* Git Details & Telemetry */}
                    <div className="mt-2.5 grid grid-cols-2 gap-2 text-[10px] text-slate-400 font-mono pt-2 border-t border-slate-800/60">
                      <div>
                        HEAD: <span className="text-slate-200">{proj.head_commit ? proj.head_commit.slice(0, 7) : "N/A"}</span>
                      </div>
                      <div>
                        Evidence: <span className="text-indigo-400 font-bold">{proj.evidence_count} records</span>
                      </div>
                      <div>
                        Commits: <span className="text-slate-200">{proj.commit_count || 0}</span>
                      </div>
                      <div>
                        Last Scan: <span className="text-slate-300">{proj.last_scanned_at ? new Date(proj.last_scanned_at).toLocaleDateString() : "Pending"}</span>
                      </div>
                    </div>

                    {/* Detected Tech Badges */}
                    {proj.detected_technologies && proj.detected_technologies.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {proj.detected_technologies.slice(0, 6).map((tech) => (
                          <span
                            key={tech}
                            className="px-2 py-0.5 rounded-md bg-slate-900/90 border border-slate-800 text-[10px] text-slate-300"
                          >
                            {tech}
                          </span>
                        ))}
                        {proj.detected_technologies.length > 6 && (
                          <span className="px-1.5 py-0.5 rounded-md bg-slate-900/90 text-[10px] text-slate-500">
                            +{proj.detected_technologies.length - 6} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Evidence Explorer Column (7 cols) */}
          <div className="lg:col-span-7">
            {selectedProject ? (
              <div className="p-5 rounded-xl bg-surface border border-surface-border space-y-4">
                {/* Explorer Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-surface-border">
                  <div>
                    <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                      <Layers className="w-4 h-4 text-indigo-400" />
                      Evidence Artifacts: {selectedProject.name}
                    </h2>
                    <p className="text-[11px] text-slate-400 mt-0.5 font-mono">
                      {selectedProject.repo_path}
                    </p>
                  </div>

                  {/* Filter Tabs */}
                  <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-[10px]">
                    {["ALL", "VERIFIED", "LIKELY", "WEAK"].map((lvl) => (
                      <button
                        key={lvl}
                        onClick={() => setEvidenceFilter(lvl)}
                        className={`px-2 py-0.5 rounded font-medium transition ${
                          evidenceFilter === lvl
                            ? "bg-indigo-600 text-white"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {lvl}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Evidence Item List */}
                {loadingEvidence ? (
                  <div className="p-8 text-center text-slate-400 text-xs">
                    <RefreshCw className="w-4 h-4 animate-spin mx-auto mb-2 text-indigo-400" />
                    Loading repository evidence records...
                  </div>
                ) : filteredEvidence.length === 0 ? (
                  <div className="p-8 text-center text-slate-400 text-xs">
                    No evidence records matching current filter.
                  </div>
                ) : (
                  <div className="space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
                    {filteredEvidence.map((item) => (
                      <div
                        key={item.id}
                        className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2 text-xs"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-white">{item.technology}</span>
                            <span className="text-[10px] text-slate-400 font-mono">
                              ({item.canonical_skill})
                            </span>
                            <span className="px-1.5 py-0.2 rounded bg-slate-800 text-[10px] text-slate-400 font-mono">
                              {item.evidence_type}
                            </span>
                          </div>

                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                              item.confidence_level === "VERIFIED"
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                                : item.confidence_level === "LIKELY"
                                ? "bg-sky-500/10 text-sky-400 border border-sky-500/30"
                                : item.confidence_level === "WEAK"
                                ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                                : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                            }`}
                          >
                            {item.confidence_level} ({Math.round(item.confidence * 100)}%)
                          </span>
                        </div>

                        {/* File Location */}
                        <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-mono">
                          <FileCode className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
                          <span className="text-slate-300">{item.source_file}</span>
                          {item.source_location && (
                            <span className="text-slate-500">:{item.source_location}</span>
                          )}
                        </div>

                        <p className="text-[11px] text-slate-400 leading-relaxed">
                          {item.description}
                        </p>

                        {/* Snippet preview */}
                        {item.snippet && (
                          <pre className="p-2 rounded bg-slate-950 border border-slate-900 text-[10px] font-mono text-slate-300 overflow-x-auto">
                            <code>{item.snippet}</code>
                          </pre>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 rounded-xl bg-surface border border-surface-border text-center text-slate-400 text-xs">
                Select a project on the left to inspect evidence artifacts.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Register Project Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-xl bg-surface border border-surface-border p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-surface-border">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                <FolderPlus className="w-4 h-4 text-indigo-400" />
                Register Local Repository
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white text-xs"
              >
                ✕
              </button>
            </div>

            {/* Modal Tabs */}
            <div className="flex rounded-lg bg-slate-900 p-1 border border-slate-800">
              <button
                type="button"
                onClick={() => setRegisterTab("local")}
                className={`flex-1 py-1.5 rounded text-xs font-medium transition-colors ${
                  registerTab === "local"
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Local Directory
              </button>
              <button
                type="button"
                onClick={() => setRegisterTab("github")}
                className={`flex-1 py-1.5 rounded text-xs font-medium transition-colors ${
                  registerTab === "github"
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Connect via GitHub
              </button>
            </div>

            {registerTab === "github" ? (
              <div className="p-3 rounded-lg bg-indigo-950/40 border border-indigo-800/40 text-[11px] text-indigo-300 space-y-1">
                <div className="font-semibold flex items-center gap-1.5 text-indigo-200">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>GitHub Local Agent Architecture</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  Provide your local clone directory of the GitHub repository.
                  Analysis occurs strictly locally on your machine—no source code or credentials ever leave localhost or touch Vercel.
                </p>
              </div>
            ) : (
              <p className="text-xs text-slate-400">
                Provide an absolute path to a local Git software repository on your system.
                CareerCrew runs read-only inspections with zero cloud APIs.
              </p>
            )}

            {modalError && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{modalError}</span>
              </div>
            )}

            <form onSubmit={handleRegister} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Project Name
                </label>
                <input
                  type="text"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder={registerTab === "github" ? "e.g. Resume_Matcher_Local_Agent" : "e.g. AI Customer Support Bot"}
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  {registerTab === "github" ? "Local Clone Path on Machine" : "Local Filesystem Absolute Path"}
                </label>
                <input
                  type="text"
                  value={formPath}
                  onChange={(e) => setFormPath(e.target.value)}
                  placeholder="e.g. D:\Resume Agent or /home/alex/projects/app"
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 font-mono text-[11px] focus:outline-none focus:border-indigo-500"
                />
                <span className="text-[10px] text-slate-500 mt-0.5 block">
                  Must be an existing local folder. System and root directories are strictly blocked.
                </span>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Description (Optional)
                </label>
                <textarea
                  value={formDesc}
                  onChange={(e) => setFormDesc(e.target.value)}
                  placeholder="Brief note on repository purpose..."
                  rows={2}
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition disabled:opacity-50"
                >
                  {submitting ? "Validating & Scanning..." : "Register & Scan"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
