"use client";

import { useState } from "react";
import { uploadAndExtractDocument } from "@/lib/api";
import { FileText, Upload, CheckCircle2, AlertCircle, Clock } from "lucide-react";

export default function ResumePage() {
  const [file, setFile] = useState<File | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setExtracting(true);
    setError(null);
    setResult(null);

    try {
      const res = await uploadAndExtractDocument(file);
      setResult(res.document);
    } catch (err: any) {
      setError(err.message || "Failed to parse document");
    } finally {
      setExtracting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-surface-border">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            Resume Management
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Local document parsing foundation (PDF via PyMuPDF, DOCX via python-docx)
          </p>
        </div>
        <div className="px-3 py-1 rounded-full bg-slate-800 text-slate-400 text-xs font-mono border border-slate-700">
          Phase 1 Ingestion Foundation
        </div>
      </div>

      {/* Extraction Verification Form */}
      <div className="p-6 rounded-xl bg-surface border border-surface-border shadow-xl">
        <h2 className="text-sm font-semibold text-white mb-1">
          Document Ingestion & Text Extraction Verifier
        </h2>
        <p className="text-xs text-slate-400 mb-4">
          Test extracting any candidate resume locally. Text is processed in-memory on your machine with zero cloud leaks.
        </p>

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="border-2 border-dashed border-slate-700 rounded-xl p-6 text-center hover:border-slate-600 transition-colors">
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center justify-center gap-2"
            >
              <Upload className="w-8 h-8 text-indigo-400" />
              <span className="text-sm text-slate-300 font-medium">
                {file ? file.name : "Click to select a resume (.pdf, .docx, .txt, .md)"}
              </span>
              <span className="text-xs text-slate-500">
                Max size: 10MB &bull; Handled exclusively by local PyMuPDF / python-docx
              </span>
            </label>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={!file || extracting}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-medium text-xs flex items-center gap-2 transition-colors"
            >
              {extracting ? "Extracting Locally..." : "Verify Local Extraction"}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3 rounded-lg bg-red-950/40 border border-red-800 text-xs text-red-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {result && (
          <div className="mt-6 pt-6 border-t border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Extraction Successful
              </span>
              <span className="text-xs font-mono text-slate-400">
                Latency: {result.extraction_time_ms} ms
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="text-slate-500 text-[10px]">FORMAT</div>
                <div className="text-white font-semibold uppercase">{result.document_type}</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="text-slate-500 text-[10px]">CHARACTERS</div>
                <div className="text-white font-semibold">{result.character_count}</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="text-slate-500 text-[10px]">WORDS</div>
                <div className="text-white font-semibold">{result.word_count}</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="text-slate-500 text-[10px]">PAGES</div>
                <div className="text-white font-semibold">{result.page_count ?? "N/A"}</div>
              </div>
            </div>

            <div>
              <div className="text-xs font-semibold text-slate-300 mb-2 font-mono">
                Extracted Text Preview:
              </div>
              <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono max-h-60 overflow-y-auto whitespace-pre-wrap">
                {result.extracted_text}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
