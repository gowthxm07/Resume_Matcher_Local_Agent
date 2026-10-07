"use client";

import { useState, useEffect } from "react";
import { uploadAndExtractDocument } from "@/lib/api";
import { FileText, Upload, Sparkles, X, Check, AlertCircle } from "lucide-react";

interface ResumeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAttachResume: (text: string, title: string) => void;
  currentTitle?: string;
}

const SAMPLE_ALEX = {
  title: "Alex Developer (Backend Lead)",
  text: `Alex Developer
alex.developer@example.com

PROFESSIONAL SUMMARY
Senior Backend Engineer with 5+ years of experience designing and operating resilient microservice architectures using Python, FastAPI, and PostgreSQL. Proven track record in Docker containerization and Git workflows.

TECHNICAL SKILLS
- Languages: Python, SQL
- Frameworks: FastAPI, SQLAlchemy
- Databases: PostgreSQL
- DevOps & Tools: Docker, Git, REST APIs, Microservices

WORK EXPERIENCE
Senior Software Engineer | TechFlow Systems (2022 - Present)
- Designed and deployed scalable asynchronous REST APIs utilizing FastAPI and Python.
- Managed high-concurrency PostgreSQL relational schemas and query optimizations.
- Containerized backend microservices with multi-stage Docker builds.

PROJECTS
High-Performance API Gateway
- Built an asynchronous API routing gateway with Python and FastAPI.
- Utilized PostgreSQL for persistent configuration caching and Docker for deployment.`,
};

const SAMPLE_JORDAN = {
  title: "Jordan Frontend (Evidence Gaps)",
  text: `Jordan Frontend
jordan.frontend@example.com

PROFESSIONAL SUMMARY
Frontend Developer specialized in React, Next.js, and TypeScript. Claimed to achieve 10x throughput scaling on AWS with 99.999% uptime.

TECHNICAL SKILLS
- Languages: TypeScript, JavaScript, HTML, CSS
- Frameworks: React, Next.js, Tailwind CSS
- Tools: Git, npm, Webpack

WORK EXPERIENCE
Frontend Specialist | WebDesign Studio (2023 - Present)
- Developed responsive user interfaces using React and Next.js.
- Handled client-side state management with TypeScript.

PROJECTS
Portfolio Showcase
- Static portfolio website built with Next.js and React.`,
};

export default function ResumeModal({
  isOpen,
  onClose,
  onAttachResume,
  currentTitle,
}: ResumeModalProps) {
  const [tab, setTab] = useState<"paste" | "upload" | "sample">("paste");
  const [resumeText, setResumeText] = useState("");
  const [resumeName, setResumeName] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

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

  const handleFileUpload = async (file: File) => {
    try {
      setIsUploading(true);
      setUploadError(null);
      const res = await uploadAndExtractDocument(file);
      const extractedText = res.extracted_text || res.text || "";
      const docName = file.name;
      onAttachResume(extractedText, docName);
      onClose();
    } catch (err: any) {
      setUploadError(err.message || "Failed to extract text from document");
    } finally {
      setIsUploading(false);
    }
  };

  const handlePasteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeText.trim()) return;
    const title = resumeName.trim() || "Pasted Resume";
    onAttachResume(resumeText.trim(), title);
    onClose();
  };

  const handleSelectSample = (sample: typeof SAMPLE_ALEX) => {
    onAttachResume(sample.text, sample.title);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-xl bg-surface border border-surface-border rounded-xl shadow-xl overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="resume-modal-title"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <FileText className="w-4 h-4 text-zinc-300" />
            <h2 id="resume-modal-title" className="text-base font-semibold text-white">
              Attach Resume
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
            Paste Text
          </button>
          <button
            onClick={() => setTab("upload")}
            className={`pb-2.5 border-b-2 transition-colors ${
              tab === "upload"
                ? "border-indigo-500 text-white"
                : "border-transparent text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Upload File (PDF / DOCX)
          </button>
          <button
            onClick={() => setTab("sample")}
            className={`pb-2.5 border-b-2 transition-colors ${
              tab === "sample"
                ? "border-indigo-500 text-white"
                : "border-transparent text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Sample Candidates
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4 text-sm">
          {tab === "paste" && (
            <form onSubmit={handlePasteSubmit} className="space-y-3">
              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Candidate Label / Name</label>
                <input
                  type="text"
                  value={resumeName}
                  onChange={(e) => setResumeName(e.target.value)}
                  placeholder="e.g. My Updated Resume"
                  className="w-full px-3 py-1.5 rounded-lg bg-background border border-surface-border text-white text-xs placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-zinc-400 mb-1">Resume Content</label>
                <textarea
                  rows={8}
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  placeholder="Paste raw resume text, skills, employment history, and project summaries..."
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
                  Attach Resume
                </button>
              </div>
            </form>
          )}

          {tab === "upload" && (
            <div className="space-y-4">
              {uploadError && (
                <div className="p-3 rounded-lg border border-red-500/30 bg-red-950/20 text-red-300 text-xs">
                  {uploadError}
                </div>
              )}
              <label className="border-2 border-dashed border-surface-border hover:border-zinc-500 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer text-center transition-colors bg-background/50">
                <Upload className="w-8 h-8 text-zinc-400 mb-2" />
                <span className="text-xs font-medium text-white mb-1">
                  {isUploading ? "Extracting document text locally..." : "Select Resume File"}
                </span>
                <span className="text-[11px] text-zinc-500">
                  PDF, DOCX, or TXT &bull; Processed locally with PyMuPDF & python-docx
                </span>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  className="hidden"
                  disabled={isUploading}
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload(file);
                  }}
                />
              </label>
            </div>
          )}

          {tab === "sample" && (
            <div className="space-y-3">
              <p className="text-xs text-zinc-400">
                Load pre-verified synthetic candidate profiles to test deterministic matching and anti-hallucination guardrails:
              </p>
              <div className="grid grid-cols-1 gap-2.5">
                <button
                  onClick={() => handleSelectSample(SAMPLE_ALEX)}
                  className="p-3 rounded-lg border border-surface-border bg-background hover:bg-surface-hover/80 text-left transition-colors flex items-start justify-between group"
                >
                  <div className="space-y-0.5">
                    <div className="text-xs font-medium text-white group-hover:text-indigo-300 flex items-center gap-2">
                      <span>Alex Developer</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-950/40 border border-emerald-500/30 text-emerald-300">
                        Strong Match
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400">
                      Python, FastAPI, PostgreSQL, Docker. Full repository corroboration.
                    </p>
                  </div>
                  <span className="text-xs text-zinc-500 group-hover:text-white">&rarr;</span>
                </button>

                <button
                  onClick={() => handleSelectSample(SAMPLE_JORDAN)}
                  className="p-3 rounded-lg border border-surface-border bg-background hover:bg-surface-hover/80 text-left transition-colors flex items-start justify-between group"
                >
                  <div className="space-y-0.5">
                    <div className="text-xs font-medium text-white group-hover:text-indigo-300 flex items-center gap-2">
                      <span>Jordan Frontend</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-amber-950/40 border border-amber-500/30 text-amber-300">
                        Evidence Gaps
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400">
                      React, Next.js, ungrounded AWS 99.999% claims. Triggers Fact-Checker rejections.
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
