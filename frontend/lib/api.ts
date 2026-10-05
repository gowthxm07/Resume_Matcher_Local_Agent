import {
  SystemStatusResponse,
  AgentArchitectureSummary,
  DatabaseSummary,
  ProjectResponse,
  EvidenceItem,
  SkillVerificationResult,
  EvidenceAssessment,
} from "@/types";


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

export async function registerProject(
  name: string,
  path: string,
  description?: string
): Promise<ProjectResponse> {
  const res = await fetch(`${API_BASE}/projects/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, path, description: description || "" }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Registration failed" }));
    throw new Error(errorData.detail || `Registration failed with HTTP ${res.status}`);
  }

  return res.json();
}

export async function fetchProjects(): Promise<ProjectResponse[]> {
  const res = await fetch(`${API_BASE}/projects`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch projects: HTTP ${res.status}`);
  return res.json();
}

export async function fetchProject(projectId: string): Promise<ProjectResponse> {
  const res = await fetch(`${API_BASE}/projects/${projectId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch project: HTTP ${res.status}`);
  return res.json();
}

export async function scanProject(projectId: string): Promise<ProjectResponse> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/scan`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Failed to scan project: HTTP ${res.status}`);
  return res.json();
}

export async function fetchProjectEvidence(
  projectId: string,
  technology?: string
): Promise<EvidenceItem[]> {
  const query = technology ? `?technology=${encodeURIComponent(technology)}` : "";
  const res = await fetch(`${API_BASE}/projects/${projectId}/evidence${query}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to fetch project evidence: HTTP ${res.status}`);
  return res.json();
}

export async function verifySkills(skills: string[]): Promise<SkillVerificationResult[]> {
  const res = await fetch(`${API_BASE}/projects/verify-skills`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ skills }),
  });
  if (!res.ok) throw new Error(`Failed to verify skills: HTTP ${res.status}`);
  return res.json();
}

export async function fetchAnalysisEvidence(analysisId: string): Promise<EvidenceAssessment> {
  const res = await fetch(`${API_BASE}/analysis/${analysisId}/evidence`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to fetch analysis evidence: HTTP ${res.status}`);
  return res.json();
}

