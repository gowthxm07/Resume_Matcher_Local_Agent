"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { fetchLocalAgentHealth, fetchProjects } from "@/lib/api";
import { AgentHealthResponse, ProjectResponse } from "@/types";
import CompatibilityModal from "@/components/CompatibilityModal";
import ProjectsModal from "@/components/ProjectsModal";
import PrivacyModal from "@/components/PrivacyModal";
import {
  FolderGit2,
  Shield,
  RefreshCw,
  Terminal,
} from "lucide-react";

export default function Header() {
  const [health, setHealth] = useState<AgentHealthResponse | null>(null);
  const [projectCount, setProjectCount] = useState<number>(0);
  const [isCompOpen, setIsCompOpen] = useState(false);
  const [isProjectsOpen, setIsProjectsOpen] = useState(false);
  const [isPrivacyOpen, setIsPrivacyOpen] = useState(false);

  const checkStatus = async () => {
    try {
      const [healthRes, projectsRes] = await Promise.allSettled([
        fetchLocalAgentHealth(),
        fetchProjects(),
      ]);
      if (healthRes.status === "fulfilled") setHealth(healthRes.value);
      else setHealth(null);

      if (projectsRes.status === "fulfilled") setProjectCount(projectsRes.value.length);
    } catch {
      setHealth(null);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const isReady = health?.status === "ready";

  return (
    <>
      <header className="h-14 border-b border-surface-border bg-surface/90 backdrop-blur-sm px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 select-none">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex items-center gap-2 group transition-opacity hover:opacity-90"
          >
            <span className="font-semibold text-sm tracking-tight text-white font-mono">
              CareerCrew
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-surface-border">
              local
            </span>
          </Link>
        </div>

        {/* Secondary Utility Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Compatibility Status Pill */}
          <button
            onClick={() => setIsCompOpen(true)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-mono font-medium transition-colors ${
              isReady
                ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-300 hover:bg-emerald-950/40"
                : "bg-amber-950/20 border-amber-500/30 text-amber-300 hover:bg-amber-950/40"
            }`}
            title="Inspect Local Agent Compatibility"
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isReady ? "bg-emerald-400" : "bg-amber-400 animate-pulse"
              }`}
            />
            <span className="hidden sm:inline">
              {isReady ? "Local Agent Ready" : "Local Agent Offline"}
            </span>
            <span className="sm:hidden">{isReady ? "Ready" : "Offline"}</span>
          </button>

          {/* Projects Button */}
          <button
            onClick={() => setIsProjectsOpen(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-surface-border bg-surface-hover/50 hover:bg-surface-hover text-zinc-300 hover:text-white text-xs transition-colors"
            title="Manage connected project repositories"
          >
            <FolderGit2 className="w-3.5 h-3.5 text-zinc-400" />
            <span>Projects</span>
            {projectCount > 0 && (
              <span className="text-[10px] font-mono px-1 rounded bg-zinc-800 text-zinc-400">
                {projectCount}
              </span>
            )}
          </button>

          {/* Privacy Button */}
          <button
            onClick={() => setIsPrivacyOpen(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-surface-border bg-surface-hover/30 hover:bg-surface-hover text-zinc-400 hover:text-zinc-200 text-xs transition-colors"
            title="Local privacy & air-gap architecture"
          >
            <Shield className="w-3.5 h-3.5 text-emerald-400/80" />
            <span className="hidden md:inline">100% Local</span>
          </button>
        </div>
      </header>

      {/* Modals */}
      <CompatibilityModal
        isOpen={isCompOpen}
        onClose={() => setIsCompOpen(false)}
      />
      <ProjectsModal
        isOpen={isProjectsOpen}
        onClose={() => setIsProjectsOpen(false)}
      />
      <PrivacyModal
        isOpen={isPrivacyOpen}
        onClose={() => setIsPrivacyOpen(false)}
      />
    </>
  );
}
