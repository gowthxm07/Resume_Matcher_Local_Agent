export interface OllamaStatus {
  reachable: boolean;
  base_url: string;
  configured_model: string;
  model_exists: boolean;
  embed_model: string;
  embed_model_exists: boolean;
  latency_ms?: number;
  error?: string | null;
}

export interface DatabaseStatus {
  connected: boolean;
  engine: string;
  status: string;
  tables: string[];
  error?: string | null;
}

export interface VectorStoreStatus {
  status: string;
  store_type: string;
  storage_path: string;
  collection_count: number;
  error?: string | null;
}

export interface SystemStatusResponse {
  backend_status: string;
  version: string;
  timestamp: string;
  local_only_verified: boolean;
  ollama: OllamaStatus;
  database: DatabaseStatus;
  vector_store: VectorStoreStatus;
}

export interface AgentSpecification {
  role: string;
  name: string;
  goal: string;
  backstory: string;
  planned_tools: string[];
  is_implemented: boolean;
  phase: number;
  llm_model: string;
}

export interface PipelineStage {
  stage: number;
  name: string;
  agents: string[];
  loop_guardrail?: string;
}

export interface AgentArchitectureSummary {
  orchestrator: string;
  framework: string;
  cloud_dependencies: string;
  pipeline_status: string;
  agent_count: number;
  agents: AgentSpecification[];
  pipeline_stages: PipelineStage[];
}

export interface DatabaseSummary {
  status: string;
  engine: string;
  counts: {
    resumes: number;
    job_descriptions: number;
    projects: number;
    applications: number;
    analysis_runs: number;
  };
}
