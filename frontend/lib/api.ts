import { SystemStatusResponse, AgentArchitectureSummary, DatabaseSummary } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export async function fetchHealth(): Promise<{ status: string; service: string; version: string }> {
  const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`);
  return res.json();
}

export async function fetchSystemStatus(): Promise<SystemStatusResponse> {
  const res = await fetch(`${API_BASE}/system/status`, { cache: "no-store" });
  if (!res.ok) throw new Error(`System status check failed: HTTP ${res.status}`);
  return res.json();
}

export async function fetchAgentArchitecture(): Promise<AgentArchitectureSummary> {
  const res = await fetch(`${API_BASE}/agents/architecture`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch agent architecture: HTTP ${res.status}`);
  return res.json();
}

export async function fetchDatabaseSummary(): Promise<DatabaseSummary> {
  const res = await fetch(`${API_BASE}/database/summary`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Database summary check failed: HTTP ${res.status}`);
  return res.json();
}

export async function testOllamaInference(prompt?: string): Promise<{
  success: boolean;
  model: string;
  response_text: string;
  latency_ms: number;
  error?: string;
}> {
  const res = await fetch(`${API_BASE}/ollama/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt: prompt || "CareerCrew local inference verification test.",
    }),
  });
  return res.json();
}

export async function uploadAndExtractDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/ingest/extract`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(errorData.detail || `Upload failed with status ${res.status}`);
  }

  return res.json();
}

export async function analyzeMatch(formData: FormData) {
  const res = await fetch(`${API_BASE}/analysis/match`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(errorData.detail || `Analysis failed with status ${res.status}`);
  }

  return res.json();
}

export async function fetchAnalysisResult(analysisId: string) {
  const res = await fetch(`${API_BASE}/analysis/${analysisId}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch analysis result: HTTP ${res.status}`);
  }

  return res.json();
}

export async function fetchRecentAnalyses() {
  const res = await fetch(`${API_BASE}/analysis/history/recent`, {
    cache: "no-store",
  });

  if (!res.ok) {
    return [];
  }

  return res.json();
}
