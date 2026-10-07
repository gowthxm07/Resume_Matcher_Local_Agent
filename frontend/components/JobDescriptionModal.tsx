"use client";

import { useState, useEffect } from "react";
import { Briefcase, X, Sparkles } from "lucide-react";

interface JobDescriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAttachJD: (text: string, title: string) => void;
  currentTitle?: string;
}

const SAMPLE_BACKEND_JD = {
  title: "Senior Python Backend Engineer",
  text: `Position: Senior Python Backend Engineer
Company: CorePlatform Cloud Solutions

About the Role:
We are seeking a Senior Python Backend Engineer to build high-performance distributed microservices.

Requirements:
- Strong proficiency in Python
- Production experience with FastAPI
- Deep relational database experience with PostgreSQL
- Familiarity with Git version control and REST APIs

Preferred Qualifications:
- Docker containerization
- Asynchronous architecture and microservices`,
};

const SAMPLE_CLOUD_JD = {
  title: "Lead Cloud Infrastructure Architect",
  text: `Position: Lead Cloud Infrastructure & Kubernetes Architect
Company: Enterprise Cloud Scale

Requirements:
- Extensive production experience with AWS cloud infrastructure
- Advanced container orchestration with Kubernetes and Helm
- Infrastructure as Code using Terraform
- Deep understanding of distributed systems architecture

Preferred:
- Golang or Python systems programming`,
};

export default function JobDescriptionModal({
  isOpen,
  onClose,
  onAttachJD,
  currentTitle,
}: JobDescriptionModalProps) {
  const [tab, setTab] = useState<"paste" | "sample">("paste");
  const [jdText, setJdText] = useState("");
  const [jdTitle, setJdTitle] = useState("");

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!jdText.trim()) return;
    const title = jdTitle.trim() || "Target Job Description";
    onAttachJD(jdText.trim(), title);
    onClose();
  };

  const handleSelectSample = (sample: typeof SAMPLE_BACKEND_JD) => {
    onAttachJD(sample.text, sample.title);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-xl bg-surface border border-surface-border rounded-xl shadow-xl overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="jd-modal-title"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Briefcase className="w-4 h-4 text-zinc-300" />
            <h2 id="jd-modal-title" className="text-base font-semibold text-white">
              Add Job Description
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-surface-hover transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tabs */}
        <div className="px-6 pt-3 flex border-b border-surface-border gap-4 text-xs font-medium">
          <button
            onClick={() => setTab("paste")}
            className={`pb-2.5 border-b-2 transition-colors ${
              tab === "paste"
                ? "border-indigo-500 text-white"
                : "border-transparent text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Paste Description
          </button>
          <button
            onClick={() => setTab("sample")}
            className={`pb-2.5 border-b-2 transition-colors ${
              tab === "sample"
                ? "border-indigo-500 text-white"
                : "border-transparent text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Sample Roles
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4 text-sm">
          {tab === "paste" && (
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Role / Job Title</label>
                <input
                  type="text"
                  value={jdTitle}
                  onChange={(e) => setJdTitle(e.target.value)}
                  placeholder="e.g. Senior Backend Engineer"
                  className="w-full px-3 py-1.5 rounded-lg bg-background border border-surface-border text-white text-xs placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Job Description Requirements</label>
                <textarea
                  rows={8}
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste target job specifications, role responsibilities, required and preferred skills..."
                  className="w-full px-3 py-2 rounded-lg bg-background border border-surface-border text-white text-xs placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500 font-mono leading-relaxed"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-3 py-1.5 rounded-lg text-xs text-zinc-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
                >
                  Attach Job Description
                </button>
              </div>
            </form>
          )}

          {tab === "sample" && (
            <div className="space-y-3">
              <p className="text-xs text-zinc-400">
                Select a benchmark job description to evaluate matching and ATS analysis:
              </p>
              <div className="grid grid-cols-1 gap-2.5">
                <button
                  onClick={() => handleSelectSample(SAMPLE_BACKEND_JD)}
                  className="p-3 rounded-lg border border-surface-border bg-background hover:bg-surface-hover/80 text-left transition-colors flex items-start justify-between group"
                >
                  <div className="space-y-0.5">
                    <div className="text-xs font-medium text-white group-hover:text-indigo-300">
                      Senior Python Backend Engineer
                    </div>
                    <p className="text-[11px] text-zinc-400">
                      CorePlatform Cloud Solutions &bull; Python, FastAPI, PostgreSQL, Git, Docker
                    </p>
                  </div>
                  <span className="text-xs text-zinc-500 group-hover:text-white">&rarr;</span>
                </button>

                <button
                  onClick={() => handleSelectSample(SAMPLE_CLOUD_JD)}
                  className="p-3 rounded-lg border border-surface-border bg-background hover:bg-surface-hover/80 text-left transition-colors flex items-start justify-between group"
                >
                  <div className="space-y-0.5">
                    <div className="text-xs font-medium text-white group-hover:text-indigo-300">
                      Lead Cloud Infrastructure & Kubernetes Architect
                    </div>
                    <p className="text-[11px] text-zinc-400">
                      Enterprise Cloud Scale &bull; AWS, Kubernetes, Terraform, Distributed Systems
                    </p>
                  </div>
                  <span className="text-xs text-zinc-500 group-hover:text-white">&rarr;</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
