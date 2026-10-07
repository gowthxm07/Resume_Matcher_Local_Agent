"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Shield, Lock, Cpu, HardDrive, WifiOff, X, ArrowUpRight } from "lucide-react";

interface PrivacyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function PrivacyModal({ isOpen, onClose }: PrivacyModalProps) {
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="w-full max-w-lg bg-surface border border-surface-border rounded-xl shadow-xl overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="privacy-modal-title"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Shield className="w-4 h-4 text-emerald-400" />
            <h2 id="privacy-modal-title" className="text-base font-semibold text-white">
              Local Privacy Guarantee
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-surface-hover transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4 text-xs text-zinc-300">
          <div className="p-3.5 rounded-lg border border-emerald-500/30 bg-emerald-950/20 text-emerald-300 font-mono flex items-center gap-2.5">
            <Lock className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>100% LOCAL EXECUTION &bull; ZERO DATA LEAVES YOUR DEVICE</span>
          </div>

          <p className="text-zinc-400 text-sm leading-relaxed">
            CareerCrew is designed from the ground up for strict confidentiality. Your resume, target job descriptions, source code repositories, and career analysis are never sent to external servers.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            <div className="p-3 rounded-lg border border-surface-border bg-background space-y-1.5">
              <div className="flex items-center gap-2 font-medium text-white">
                <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                <span>Local AI Inference</span>
              </div>
              <p className="text-[11px] text-zinc-400 leading-normal">
                Executed via Ollama (Llama 3.2:3b) on your local CPU/GPU. No OpenAI, Anthropic, or cloud API keys.
              </p>
            </div>

            <div className="p-3 rounded-lg border border-surface-border bg-background space-y-1.5">
              <div className="flex items-center gap-2 font-medium text-white">
                <HardDrive className="w-3.5 h-3.5 text-indigo-400" />
                <span>Local Storage</span>
              </div>
              <p className="text-[11px] text-zinc-400 leading-normal">
                Persisted in local SQLite database and ChromaDB vector store on your filesystem.
              </p>
            </div>

            <div className="p-3 rounded-lg border border-surface-border bg-background space-y-1.5">
              <div className="flex items-center gap-2 font-medium text-white">
                <WifiOff className="w-3.5 h-3.5 text-indigo-400" />
                <span>Air-Gap Ready</span>
              </div>
              <p className="text-[11px] text-zinc-400 leading-normal">
                Functions without an active internet connection once initial local models are pulled.
              </p>
            </div>

            <div className="p-3 rounded-lg border border-surface-border bg-background space-y-1.5">
              <div className="flex items-center gap-2 font-medium text-white">
                <Lock className="w-3.5 h-3.5 text-indigo-400" />
                <span>Host Isolation</span>
              </div>
              <p className="text-[11px] text-zinc-400 leading-normal">
                FastAPI agent strictly bound to 127.0.0.1 with strict CORS origins.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-surface-border bg-surface-hover/20 flex items-center justify-between text-xs">
          <Link
            href="/privacy"
            onClick={onClose}
            className="text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center gap-1 transition-colors"
          >
            <span>View Technical Data Processing Matrix</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white font-medium transition-colors"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
