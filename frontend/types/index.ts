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

export interface FactualClaim {
  claim_id: string;
  text: string;
  category: string;
  section: string;
  source: string;
  evidence_ids: string[];
  confidence: number;
  status: "SUPPORTED" | "PARTIALLY_SUPPORTED" | "UNSUPPORTED" | "CONTRADICTED" | string;
  notes?: string | null;
}

export interface OptimizationChange {
  change_id: string;
  section: string;
  original_text: string;
  proposed_text: string;
  reason: string;
  change_type: string;
  evidence_ids: string[];
  related_jd_requirements: string[];
  expected_impact: string;
  claims: FactualClaim[];
  status: "PENDING" | "SUPPORTED" | "PARTIALLY_SUPPORTED" | "UNSUPPORTED" | "CONTRADICTED" | "ACCEPTED" | "REJECTED" | string;
  rejection_reason?: string | null;
  fact_check_status?: string;
  fact_check_reason?: string;
  grounding_evidence_ids?: string[];
}

export interface ATSValidationResult {
  overall_ats_score: number;
  parseability_score: number;
  section_structure_score: number;
  required_skill_coverage_score: number;
  preferred_skill_coverage_score: number;
  keyword_distribution_score: number;
  formatting_safety_score: number;
  identified_sections: string[];
  missing_standard_sections: string[];
  matched_required_skills: string[];
  missing_required_skills: string[];
  matched_preferred_skills: string[];
  missing_preferred_skills: string[];
  detected_stuffing_keywords: string[];
  formatting_hazards: string[];
  is_ats_compliant: boolean;
  disclaimer: string;
}

export interface ResumeVersionSchema {
  id: string;
  resume_id: string;
  parent_version_id?: string | null;
  analysis_id?: string | null;
  iteration: number;
  content: string;
  match_score?: number | null;
  ats_score?: number | null;
  evidence_confidence?: number | null;
  status: "ORIGINAL" | "CANDIDATE" | "ACCEPTED" | "REJECTED" | "FINAL" | string;
  change_summary?: Record<string, any>;
  audit_trail: Record<string, any>[];
  created_at: string;
}

export interface OptimizationIterationResult {
  iteration: number;
  proposals_count: number;
  accepted_changes_count: number;
  rejected_changes_count: number;
  baseline_match_score: number;
  iteration_match_score: number;
  baseline_ats_score: number;
  iteration_ats_score: number;
  evidence_confidence_score: number;
  status: string;
  changes: OptimizationChange[];
  rejected_claims: Record<string, any>[];
}

export interface OptimizationDossier {
  analysis_id: string;
  resume_id: string;
  job_description_id: string;
  baseline_version_id: string;
  final_version_id: string;
  iterations_run: number;
  max_iterations: number;
  baseline_match_score: number;
  final_match_score: number;
  baseline_ats_score: number;
  final_ats_score: number;
  baseline_evidence_confidence: number;
  final_evidence_confidence: number;
  total_proposed_changes: number;
  total_accepted_changes: number;
  total_rejected_changes: number;
  accepted_changes: OptimizationChange[];
  rejected_changes: OptimizationChange[];
  audit_trail: Record<string, any>[];
  ats_validation: ATSValidationResult;
  iterations: OptimizationIterationResult[];
  score_improvement: number;
  ats_improvement: number;
  disclaimer: string;
  created_at: string;
}

export interface OptimizeRequest {
  resume_id?: string | null;
  job_description_id?: string | null;
  project_ids?: string[];
  max_iterations?: number;
  raw_resume_text?: string | null;
  raw_jd_text?: string | null;
  use_live_llm?: boolean;
}

export interface OptimizeResponse {
  run_id: string;
  dossier: OptimizationDossier;
  final_version: ResumeVersionSchema;
  versions: ResumeVersionSchema[];
}

export type CompatibilityStatus =
  | "READY"
  | "MISSING"
  | "OUTDATED"
  | "ERROR"
  | "OPTIONAL"
  | "CHECKING";

export interface CompatibilityCheckItem {
  name: string;
  status: CompatibilityStatus;
  required: boolean;
  detected_version?: string | null;
  required_version?: string | null;
  message: string;
  setup_route?: string | null;
}

export interface CompatibilityResponse {
  ready: boolean;
  checks: CompatibilityCheckItem[];
  agent_version: string;
  timestamp: string;
}

export interface AgentHealthResponse {
  agent: string;
  status: string;
  version: string;
  api_version: string;
  local_only: boolean;
}

export interface AgentCapabilitiesResponse {
  analysis: boolean;
  multi_agent: boolean;
  evidence_scanning: boolean;
  resume_optimization: boolean;
  fact_checking: boolean;
  ats_validation: boolean;
  github_import: boolean;
  interview_intelligence: boolean;
}



