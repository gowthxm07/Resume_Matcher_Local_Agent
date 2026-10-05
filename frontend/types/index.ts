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

export interface RequirementMatchResult {
  canonical_skill: string;
  original_text: string;
  requirement_type: "required" | "preferred";
  classification?: "match" | "partial_match" | "missing";
  status?: "match" | "partial_match" | "missing";
  confidence: number;
  candidate_evidence?: string[];
  evidence?: string;
  explanation: string;
  extracted_source?: string;
}

export interface DimensionScores {
  overall_score?: number;
  required_skill_score: number;
  preferred_skill_score: number;
  technical_depth_score: number;
  project_relevance_score: number;
  experience_alignment_score?: number;
  education_alignment_score?: number;
  keyword_coverage_score?: number;
  experience_score?: number;
  education_score?: number;
  keyword_score?: number;
  weights?: Record<string, number>;
}

export interface ProjectRelevanceItem {
  project_name: string;
  technologies?: string[];
  similarity_score: number;
  matched_themes?: string[];
  matched_skills?: string[];
  overlap_summary?: string;
}

export interface AnalysisMetadata {
  llm_provider?: string;
  model?: string;
  model_name?: string;
  embedding_model: string;
  raw_text_hashes?: Record<string, string>;
  extraction_time_ms: number;
  matching_time_ms?: number;
  analysis_time_ms?: number;
  inference_time_ms: number;
  total_time_ms: number;
  timestamp: string;
}

export interface AnalysisResult {
  overall_score: number;
  match_classification?: "Strong Match" | "Moderate Match" | "Poor Match";
  summary?: string;
  summary_explanation?: string;
  dimension_scores: DimensionScores;
  scoring_weights?: Record<string, number>;
  requirements_analysis: RequirementMatchResult[];
  matched_requirements: RequirementMatchResult[];
  partial_matches?: RequirementMatchResult[];
  partial_requirements?: RequirementMatchResult[];
  missing_requirements: RequirementMatchResult[];
  strong_areas?: string[];
  weak_areas?: string[];
  project_relevance: ProjectRelevanceItem[];
  metadata: AnalysisMetadata;
  analysis_run_id?: string;
  resume_id?: string;
  job_description_id?: string;
}

