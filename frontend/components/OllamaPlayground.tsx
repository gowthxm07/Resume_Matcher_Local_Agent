"use client";

import { useState } from "react";
import { testOllamaInference } from "@/lib/api";
import { Terminal, Send, CheckCircle2, AlertCircle, Clock } from "lucide-react";

export default function OllamaPlayground() {
  const [prompt, setPrompt] = useState(
    "Verify local LLM operational status in 1 sentence."
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    model: string;
    response_text: string;
    latency_ms: number;
    error?: string;
  } | null>(null);

  const handleTest = async () => {
    setLoading(true);
    try {
      const data = await testOllamaInference(prompt);
      setResult(data);
    } catch (err: any) {
      setResult({
        success: false,
        model: "llama3.2:3b",
        response_text: "",
        latency_ms: 0,
        error: err.message || "Failed to reach backend",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 rounded-xl bg-surface border border-surface-border shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-surface-border">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-semibold text-white">
            Local LLM Verification Console
          </h3>
        </div>
        <span className="text-xs font-mono text-slate-400">
          Target: http://localhost:11434 (llama3.2:3b)
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-4">
        Send a real test prompt to the locally running Ollama instance to measure inference latency and verify zero-cloud execution.
      </p>

      <div className="flex gap-3 mb-4">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter prompt for local Llama 3.2:3b..."
          className="flex-1 px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono"
        />
        <button
          onClick={handleTest}
          disabled={loading || !prompt.trim()}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-medium text-sm flex items-center gap-2 transition-colors"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
              Inferring...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Send className="w-4 h-4" />
              Test Local Inference
            </span>
          )}
        </button>
      </div>

      {result && (
        <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono">
          <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-900">
            <div className="flex items-center gap-2">
              {result.success ? (
                <span className="flex items-center gap-1 text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" /> Inference Successful
                </span>
              ) : (
                <span className="flex items-center gap-1 text-red-400">
                  <AlertCircle className="w-4 h-4" /> Inference Failed
                </span>
              )}
              <span className="text-slate-500">|</span>
              <span className="text-slate-400">Model: {result.model}</span>
            </div>
            <div className="flex items-center gap-1 text-indigo-400">
              <Clock className="w-3.5 h-3.5" />
              <span>{result.latency_ms} ms</span>
            </div>
          </div>

          {result.success ? (
            <div className="text-slate-200 whitespace-pre-wrap leading-relaxed">
              {result.response_text}
            </div>
          ) : (
            <div className="text-red-400">
              {result.error || "Unknown error communicating with local LLM"}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
