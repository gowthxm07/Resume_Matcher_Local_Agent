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
  evidence_assessment?: EvidenceAssessment;
}

export type ConfidenceLevel = "VERIFIED" | "LIKELY" | "WEAK" | "UNVERIFIED";

export interface EvidenceItem {
  id: string;
  project_id: string;
  project_name?: string;
  technology: string;
  canonical_skill: string;
  evidence_type: string;
  source_file: string;
  source_location?: string | null;
  description: string;
  confidence: number;
  confidence_level: ConfidenceLevel;
  detector: string;
  snippet?: string | null;
  created_at?: string;
}

export interface ProjectResponse {
  id: string;
  name: string;
  description: string;
  repo_path: string;
  status: string;
  git_remote?: string | null;
  git_branch?: string | null;
  head_commit?: string | null;
  commit_count?: number;
  last_scanned_at?: string | null;
  evidence_count: number;
  detected_technologies: string[];
  created_at: string;
}

export interface SkillVerificationResult {
  skill: string;
  canonical_skill: string;
  status: ConfidenceLevel;
  confidence: number;
  projects: string[];
  evidence_count: number;
  evidence_records: EvidenceItem[];
  summary: string;
}

export interface EvidenceChainItem {
  requirement: string;
  canonical_skill: string;
  requirement_type: string;
  resume_claimed: boolean;
  resume_evidence?: string | null;
  projects_found: string[];
  verification_status: ConfidenceLevel;
  verification_confidence: number;
  repository_evidence: EvidenceItem[];
  rationale: string;
}

export interface EvidenceAssessment {
  evidence_confidence_score: number;
  verified_skills_count: number;
  likely_skills_count: number;
  weak_skills_count: number;
  unverified_skills_count: number;
  evidence_coverage_percentage: number;
  chain: EvidenceChainItem[];
  scanned_projects_count: number;
  timestamp: string;
}

export interface AgentExecutionTelemetry {
  agent_name: string;
  task_name: string;
  start_time: string;
  end_time: string;
  duration_ms: number;
  llm_invocations: number;
  tool_invocations: number;
  status: string;
  error?: string | null;
}

export interface AgentExecutionSummary {
  total_duration_ms: number;
  total_llm_invocations: number;
  total_tool_invocations: number;
  execution_mode: string;
  agents_active: string[];
  agents_inactive: string[];
  telemetry: AgentExecutionTelemetry[];
}

export interface FinalAnalysisDossier {
  analysis_id: string;
  resume_id: string;
  job_description_id: string;
  overall_match_score: number;
  evidence_confidence_score: number;
  classification: "STRONG_FIT" | "POTENTIAL_FIT" | "WEAK_FIT" | "NOT_RECOMMENDED" | string;
  dimension_scores: Record<string, number>;
  critical_requirements: string[];
  strong_matches: string[];
  partial_matches: string[];
  missing_requirements: string[];
  verified_skills: string[];
  unverified_skills: string[];
  project_evidence: Record<string, any>[];
  key_strengths: string[];
  key_gaps: string[];
  agent_execution_summary?: AgentExecutionSummary;
  timing_information?: Record<string, number>;
  created_at: string;
}

export interface BenchmarkComparisonResult {
  resume_id: string;
  job_description_id: string;
  baseline_match_score: number;
  crew_match_score: number;
  evidence_confidence_score: number;
  baseline_execution_ms: number;
  crew_execution_ms: number;
  baseline_llm_calls: number;
  crew_llm_calls: number;
  baseline_tool_calls: number;
  crew_tool_calls: number;
  baseline_missing_requirements_count: number;
  crew_missing_requirements_count: number;
  score_differential: number;
  synthesis_insights: string[];
}



