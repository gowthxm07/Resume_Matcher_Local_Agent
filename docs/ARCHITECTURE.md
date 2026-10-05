# CareerCrew System Architecture

## 1. Architectural Philosophy

CareerCrew is engineered around three non-negotiable principles:
1. **Zero External Paid Cloud APIs**: All inference, embeddings, and vector indexing must run locally on consumer hardware.
2. **Zero Hallucination / Grounded Reality**: The optimizer may only elevate and highlight accomplishments verifiable in the candidate's original resume or genuine local project repositories.
3. **Decoupled Service Boundaries**: Clear layers isolate document parsing, local inference, persistence, and multi-agent coordination so that LLMs or vector stores can be replaced without refactoring business logic.

---

## 2. Monorepo Layer Decomposition

```
[ Frontend: Next.js 14 App Router ]
           │  (REST JSON over HTTP, port 3000 -> 8000)
           ▼
[ API Gateway: FastAPI v1 ]
    ├── /api/health              (Fast liveness check)
    ├── /api/system/status       (Telemetry: Ollama, DB, Vector Store)
    ├── /api/ingest/extract      (Local PDF/DOCX/TXT text extractor)
    ├── /api/agents/architecture (Multi-agent team blueprint)
    ├── /api/ollama/test         (Local LLM inference verification)
    └── /api/database/summary    (Entity count audit)
           │
           ├── Core Services
           │    ├── OllamaService (local LLM client, latency measurement)
           │    ├── EmbeddingService (Ollama nomic-embed-text)
           │    └── ChromaVectorStore (local disk vector index)
           │
           ├── Ingestion Engine
           │    ├── PDFExtractor (PyMuPDF / pymupdf)
           │    ├── DOCXExtractor (python-docx)
           │    ├── TextExtractor (UTF-8/fallback plain text & markdown)
           │    └── DocumentParser (Path sanitization & file size limits)
           │
           ├── Data Access Layer
           │    ├── SQLAlchemy 2.0 ORM
           │    └── SQLite (./data/database/careercrew.db)
           │
           └── Multi-Agent Layer (CrewAI)
                └── CareerCrewOrchestrator (9 specialized agents)
```

---

## 3. CrewAI Multi-Agent Architecture

The CareerCrew multi-agent team uses specialized roles orchestrated through a sequential and looped execution pattern.

### The 9 Specialized Agents

| Agent Name | Role | Goal & Responsibilities | Planned Tools |
| :--- | :--- | :--- | :--- |
| **Manager Agent** | Orchestrator | Coordinates team execution, monitors convergence in optimization loops, compiles final candidate dossier. | `delegate_task`, `evaluate_convergence`, `compile_dossier` |
| **JD Analyzer Agent** | Requirements Specialist | Deconstructs job descriptions into hard skills, soft skills, seniority indicators, and weighted priorities. | `extract_technical_skills`, `rank_requirement_weights`, `identify_domain_jargon` |
| **Resume Analyzer Agent** | Candidate Auditor | Parses applicant resumes into chronological experiences, bullet points, asserted skills, and quantifiable metrics. | `extract_work_history`, `extract_claimed_skills`, `parse_bullet_metrics` |
| **Evidence Agent** | Code Forensic Inspector | Scans local git repositories, commit history, and code patterns to extract genuine proof for claimed proficiencies. | `scan_git_repository`, `extract_commit_evidence`, `index_code_signatures` |
| **Match Analyzer Agent** | Gap & Fit Auditor | Calculates semantic overlap between applicant claims and job requirements; surfaces coverage gaps. | `compute_match_score`, `identify_coverage_gaps`, `rank_priority_alignments` |
| **Resume Optimizer Agent** | Accomplishment Writer | Refactors bullet points to emphasize verified achievements matching target role language without inventing claims. | `refactor_bullet_xyz_format`, `inject_verified_evidence`, `align_tone` |
| **Fact Checker Agent** | Anti-Hallucination Guardrail | **Critical Safety Barrier.** Rigorously cross-references rewritten bullets against original resume + project code. Rejects unverified assertions. | `verify_claim_entailment`, `detect_fabricated_metrics`, `flag_unverified_skills` |
| **ATS Validator Agent** | Format & Parser Emulator | Emulates enterprise ATS parsers (Taleo, Greenhouse, Workday) to verify keyword placement, header hierarchy, and parseability. | `simulate_ats_parser`, `audit_section_hierarchy`, `check_keyword_density` |
| **Interview Agent** | Technical & STAR Coach | Generates role-specific technical deep dives and STAR-format behavioral interview questions grounded in candidate's real project evidence. | `generate_technical_questions`, `generate_star_scenarios`, `evaluate_mock_answers` |

### Pipeline Execution Stages

```mermaid
flowchart TD
    subgraph Stage1["Stage 1: Deconstruction & Evidence Scanning"]
        A1["Resume Document"] --> RA["Resume Analyzer Agent"]
        A2["Job Description"] --> JA["JD Analyzer Agent"]
        A3["Local Git Repos"] --> EA["Evidence Agent"]
    end

    subgraph Stage2["Stage 2: Baseline Assessment"]
        RA --> MA["Match Analyzer Agent"]
        JA --> MA
        EA --> MA
        MA --> BS["Initial Fit & Gap Matrix"]
    end

    subgraph Stage3["Stage 3: Zero-Hallucination Iteration Loop"]
        BS --> RO["Resume Optimizer Agent"]
        RO --> FC["Fact Checker Agent"]
        FC -->|"Claim Unverified / Hallucination"| RO
        FC -->|"Verified Grounded Claim"| AV["ATS Validator Agent"]
        AV -->|"Formatting / Keyword Deficiency"| RO
        AV -->|"Passed ATS Verification"| OPT["Optimized Tailored Resume"]
    end

    subgraph Stage4["Stage 4: Dossier & Interview Prep"]
        OPT --> IA["Interview Agent"]
        OPT --> MGR["Manager Agent"]
        IA --> DOS["Final Application Dossier + STAR Prep"]
        MGR --> DOS
    end
```

---

## 4. Local Ollama & Embedding Integration

- **Inference Client**: Encapsulated in `app.services.OllamaService`. Sends asynchronous HTTP requests to `http://localhost:11434/api/generate` with `stream: false`.
- **Latency & Telemetry**: Every call records nanosecond duration and eval token counts to ensure performance transparency.
- **Model Isolation**: Standardized on `llama3.2:3b`. Runs comfortably on modest hardware (low VRAM / CPU fallback).
- **Local Embeddings**: `app.services.EmbeddingService` interfaces with Ollama's `/api/embeddings` utilizing `nomic-embed-text` (768 dimensions). No external calls to OpenAI or remote embedding APIs.

---

## 5. Local Vector Store (ChromaDB)

- **Engine**: Chroma persistent client embedded in Python.
- **Directory**: `./data/embeddings/chroma`
- **Abstraction**: `VectorStoreBase` defines abstract methods (`add_texts`, `query`, `get_stats`) allowing clean substitution with FAISS or alternative local vector backends.
- **Privacy**: Chroma telemetry is explicitly disabled (`anonymized_telemetry: False`).

---

## 6. Local SQLite Database Foundation

Schema defined with SQLAlchemy 2.0 in `app.models`:
- **Resume**: `id`, `filename`, `file_path`, `file_type`, `file_size_bytes`, `raw_text`, `status`, `parsed_metadata`, `created_at`, `updated_at`.
- **JobDescription**: `id`, `title`, `company`, `raw_text`, `source_url`, `status`, `parsed_metadata`, `created_at`, `updated_at`.
- **Project**: `id`, `name`, `description`, `repo_path`, `status`, `evidence_metadata`, `created_at`, `updated_at`.
- **Application**: `id`, `resume_id` (FK), `job_description_id` (FK), `target_role`, `company_name`, `status`, `notes`.
- **AnalysisRun**: `id`, `resume_id` (FK), `job_description_id` (FK), `application_id` (FK), `run_type`, `status`, `match_score`, `results_summary`, `error_message`, `started_at`, `completed_at`.

---

## 7. Document Ingestion & Sanitization

- **PDF Extraction**: PyMuPDF (`pymupdf`) extracts text blocks, page numbers, and embedded metadata. Encrypted/password-protected PDFs are detected and rejected.
- **DOCX Extraction**: `python-docx` parses paragraphs, bullet items, and table contents (often used for layout in technical resumes).
- **Text & Markdown Extraction**: TextExtractor handles `.txt` and `.md` with multi-encoding fallback (`utf-8`, `utf-8-sig`, `latin-1`).
- **Path Sanitization**: `sanitize_filename` strips path traversal (`../../`), null bytes (`\x00`), and unsafe shell characters.
- **Size Enforcement**: Configurable `UPLOAD_MAX_BYTES` (default 10MB) prevents resource exhaustion.

---

## 8. Phase 2: Document Intelligence & Explainable Match Engine

Phase 2 introduces the intelligence layer that transforms unstructured resume and job description documents into structured schemas and computes transparent, multidimensional match scores with zero hallucinations.

### 8.1 Structured Profile Extractor (`app.services.extractor_service`)
- **LLM-Powered Extraction**: Queries local Ollama (`llama3.2:3b`) with structured JSON schemas and strict anti-hallucination prompts.
- **Resilient JSON Recovery**: Handles markdown code fences (` ```json `), outermost brace peeling, and trailing comma repair without throwing parse exceptions.
- **Deterministic Regex Fallback**: If Ollama is offline or generates invalid JSON, fallback parsers extract contacts, catalog skills, experience, and projects using deterministic heuristics.
- **SHA-256 Content Hash Caching**: Caches parsed `ResumeProfile` and `JobProfile` in memory keyed by text hash, eliminating redundant local LLM calls.

### 8.2 Canonical Skill Normalizer (`app.services.skill_normalizer`)
- **Canonical Skill Taxonomy**: Maps thousands of tech skill aliases to standard canonical IDs (e.g., `JS` -> `JavaScript`, `Postgres` -> `PostgreSQL`, `k8s` -> `Kubernetes`).
- **Strict Negative Boundaries**: Enforces negative boundaries to prevent false equivalences:
  - `Java` != `JavaScript`
  - `C` != `C++` != `C#`
  - `TypeScript` != `JavaScript`
- **Categorization**: Groups normalized skills into `PROGRAMMING_LANGUAGE`, `FRAMEWORK`, `DATABASE`, `CLOUD`, `DEVOPS`, `TOOL`, `ARCHITECTURE`, `TESTING`, `SOFT_SKILL`, `EDUCATION`, and `EXPERIENCE`.

### 8.3 Requirement Classifier (`app.services.requirement_classifier`)
- **Categorization**: Distinguishes `REQUIRED` (mandatory) vs `PREFERRED` (nice-to-have) requirements using keyword heuristics.
- **Experience Requirement Extraction**: Regex parsing extracts minimum required years of experience (e.g. "5+ years" -> `5.0`).
- **Importance Weighting**: Assigns `critical`, `high`, `medium`, or `low` based on phrasing intensity and category.

### 8.4 Semantic Project Relevance (`app.services.project_relevance`)
- **Local Dense Embeddings**: Computes cosine similarity between candidate project descriptions and job description responsibilities using Ollama `nomic-embed-text`.
- **Lexical Overlap Fallback**: Jaccard similarity fallback if embedding generation fails.
- **Matched Technology Attribution**: Highlights specific candidate technologies utilized in projects that overlap with target job requirements.

### 8.5 Explainable Matching Engine (`app.services.matching_engine`)
Computes an explainable composite match score strictly bounded between `[0.0, 100.0]`:

$$\text{Overall Score} = \sum_{i=1}^{7} w_i \times S_i$$

Where weights $w_i$ sum to $1.0$ (100%):
1. **Required Skill Coverage (35%)**: Direct coverage of mandatory skills ($1.0$ for MATCH, $0.5$ for PARTIAL).
2. **Preferred Skill Coverage (15%)**: Coverage of bonus and preferred qualifications.
3. **Technical Depth (15%)**: Verified usage of skills in work experience and projects vs mere keyword listing.
4. **Project Semantic Relevance (15%)**: Alignment between candidate project accomplishments and target role responsibilities.
5. **Experience Alignment (10%)**: Total verified experience vs required minimum years.
6. **Education Alignment (5%)**: Degree and field of study alignment.
7. **Keyword Coverage (5%)**: Overlap across general technical domain terms.

Every job requirement is classified into:
- **`MATCH`**: Clear candidate competency with grounded evidence.
- **`PARTIAL_MATCH`**: Related or adjacent experience without exact requirement satisfaction.
- **`MISSING`**: True requirement gap requiring candidate skill development.

