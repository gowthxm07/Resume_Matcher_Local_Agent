"use client";

import { useState, useEffect } from "react";
import { fetchProjects, registerProject, scanProject } from "@/lib/api";
import { ProjectResponse } from "@/types";
import {
  FolderGit2,
  Plus,
  RefreshCw,
  X,
  CheckCircle2,
  Clock,
  FolderOpen,
  ArrowRight,
  Code2,
  FileCode2,
} from "lucide-react";

interface ProjectsModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedProjectId?: string | null;
  onSelectProject?: (project: ProjectResponse) => void;
}

export default function ProjectsModal({
  isOpen,
  onClose,
  selectedProjectId,
  onSelectProject,
}: ProjectsModalProps) {
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [scanningId, setScanningId] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const [name, setName] = useState("");
  const [path, setPath] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchProjects();
      setProjects(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch projects");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadProjects();
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

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !path.trim()) {
      setError("Project name and absolute path are required.");
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const newProj = await registerProject(name.trim(), path.trim(), description.trim());
      setSuccessMsg(`Project "${newProj.name}" registered successfully.`);
      setName("");
      setPath("");
      setDescription("");
      setIsAdding(false);
      await loadProjects();
      if (onSelectProject) onSelectProject(newProj);
    } catch (err: any) {
      setError(err.message || "Failed to register project");
    } finally {
      setLoading(false);
    }
  };

  const handleScan = async (projectId: string) => {
    try {
      setScanningId(projectId);
      setError(null);
      await scanProject(projectId);
      setSuccessMsg("Repository scan completed successfully.");
      await loadProjects();
    } catch (err: any) {
      setError(err.message || "Failed to scan repository");
    } finally {
      setScanningId(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-xl bg-surface border border-surface-border rounded-xl shadow-xl overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="projects-modal-title"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <FolderGit2 className="w-4 h-4 text-zinc-300" />
            <h2 id="projects-modal-title" className="text-base font-semibold text-white">
              Project Repositories
            </h2>
            <span className="text-xs font-mono text-zinc-500">
              ({projects.length} connected)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsAdding(!isAdding)}
              className="px-2.5 py-1 text-xs font-medium rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>{isAdding ? "Cancel" : "Add Repository"}</span>
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
        <div className="p-6 overflow-y-auto space-y-4 text-sm">
          {error && (
            <div className="p-3 rounded-lg border border-red-500/30 bg-red-950/20 text-red-300 text-xs">
              {error}
            </div>
          )}
          {successMsg && (
            <div className="p-3 rounded-lg border border-emerald-500/30 bg-emerald-950/20 text-emerald-300 text-xs flex items-center justify-between">
              <span>{successMsg}</span>
              <button
                onClick={() => setSuccessMsg(null)}
                className="text-emerald-400 hover:text-emerald-200 text-xs"
              >
                &times;
              </button>
            </div>
          )}

          {/* Add repository form */}
          {isAdding && (
            <form onSubmit={handleRegister} className="p-4 rounded-lg border border-surface-border bg-background space-y-3">
              <div className="text-xs font-medium text-white">Register Local Git Repository</div>
              <div className="space-y-2">
                <div>
                  <label className="block text-[11px] text-zinc-400 mb-1">Project Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Resume Matcher Agent"
                    className="w-full px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-white text-xs placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-zinc-400 mb-1">Absolute Directory Path</label>
                  <input
                    type="text"
                    value={path}
                    onChange={(e) => setPath(e.target.value)}
                    placeholder="e.g. D:\Projects\my-repo"
                    className="w-full px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-white text-xs font-mono placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-zinc-400 mb-1">Description (Optional)</label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Brief description of tech stack and role"
                    className="w-full px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-white text-xs placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setIsAdding(false)}
                  className="px-3 py-1.5 rounded-lg text-xs text-zinc-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
                >
                  {loading ? "Registering..." : "Connect Repository"}
                </button>
              </div>
            </form>
          )}

          {/* Connected Repositories List */}
          <div className="space-y-2">
            <div className="text-xs font-medium uppercase tracking-wider text-zinc-400 px-0.5">
              Connected Repositories
            </div>

            {loading && projects.length === 0 ? (
              <div className="p-8 text-center text-xs text-zinc-500">Loading repositories...</div>
            ) : projects.length === 0 ? (
              <div className="p-8 text-center border border-dashed border-surface-border rounded-lg text-xs text-zinc-500">
                <p>No local repositories connected yet.</p>
                <button
                  onClick={() => setIsAdding(true)}
                  className="mt-2 text-indigo-400 hover:underline"
                >
                  + Add your first repository
                </button>
              </div>
            ) : (
              <div className="border border-surface-border rounded-lg divide-y divide-surface-border bg-background/50">
                {projects.map((proj) => {
                  const isSelected = selectedProjectId === proj.id;
                  const isScanning = scanningId === proj.id;

                  return (
                    <div
                      key={proj.id}
                      className={`p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs transition-colors ${
                        isSelected ? "bg-surface-hover/80" : "hover:bg-surface-hover/40"
                      }`}
                    >
                      <div className="space-y-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-white truncate">{proj.name}</span>
                          {isSelected && (
                            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-indigo-950/60 border border-indigo-500/40 text-indigo-300">
                              ACTIVE CONTEXT
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-zinc-400 font-mono truncate" title={proj.repo_path}>
                          {proj.repo_path}
                        </div>
                        {proj.description && (
                          <div className="text-zinc-500 text-[11px] truncate">{proj.description}</div>
                        )}
                        <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] text-zinc-400 font-mono">
                          {proj.detected_technologies && proj.detected_technologies.length > 0 && (
                            <span className="flex items-center gap-1">
                              <Code2 className="w-3 h-3 text-zinc-500" />
                              {proj.detected_technologies.slice(0, 3).join(", ")}
                            </span>
                          )}
                          {proj.evidence_count !== undefined && (
                            <span>{proj.evidence_count} evidence items</span>
                          )}
                          {proj.last_scanned_at && (
                            <span className="text-zinc-500">
                              Scanned {new Date(proj.last_scanned_at).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0 pt-2 sm:pt-0">
                        <button
                          onClick={() => handleScan(proj.id)}
                          disabled={isScanning}
                          className="p-1.5 rounded-lg border border-surface-border hover:bg-surface text-zinc-400 hover:text-white transition-colors"
                          title="Scan repository for evidence"
                        >
                          <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? "animate-spin text-indigo-400" : ""}`} />
                        </button>
                        {onSelectProject && (
                          <button
                            onClick={() => {
                              onSelectProject(proj);
                              onClose();
                            }}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                              isSelected
                                ? "bg-zinc-800 text-zinc-300 cursor-default"
                                : "bg-indigo-600 hover:bg-indigo-500 text-white"
                            }`}
                          >
                            {isSelected ? "Selected" : "Select"}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-surface-border bg-surface-hover/20 flex items-center justify-between text-xs text-zinc-500">
          <span>Git evidence is scanned locally. No code leaves your device.</span>
          <button
            onClick={loadProjects}
            className="hover:text-zinc-300 transition-colors flex items-center gap-1 text-[11px]"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>
    </div>
  );
}
