# CAREERCREW

> **Privacy-First Local Multi-Agent Job Application Optimizer**  
> *A serious, local AI career intelligence system that optimizes resumes against real job descriptions, verifies claims against actual project code, prevents AI hallucinations, and prepares candidates for interviews—with **ZERO paid cloud APIs**.*

---

## 1. Project Purpose & Philosophy

Modern job hunting exposes candidates to opaque AI screening algorithms and privacy risks. Existing "resume optimizers" are typically thin wrappers around cloud LLMs (OpenAI, Anthropic, Gemini) that upload confidential employment records, contact details, and proprietary codebases to remote servers, while often hallucinating claims to artificially boost match scores.

**CareerCrew** is built on an uncompromising **local-first, privacy-by-design architecture**:
- **Zero Paid Cloud APIs**: Runs exclusively on local hardware with **Ollama** and local open weights.
- **Strict Anti-Hallucination Guardrails**: Resumes are modified *only* by re-framing verified candidate experiences and evidence from genuine codebases. If a claim cannot be verified, it is never added.
- **Air-Gapped Operation**: Once models and dependencies are downloaded, the platform functions 100% offline with zero internet access required.
- **Local Persistent Storage**: All data, vector embeddings, parsed documents, and analysis runs remain strictly on your local disk in SQLite and ChromaDB.

---

## 2. Key Features Planned

| Capability | Description | Phase |
| :--- | :--- | :--- |
| **Local Ingestion** | Robust extraction of resumes & JDs from PDF (PyMuPDF), DOCX (python-docx), TXT, and Markdown. | **Phase 1** (Done) |
| **System Telemetry** | Real-time status inspection of local Ollama, Llama 3.2:3b, SQLite, and ChromaDB. | **Phase 1** (Done) |
| **Multi-Agent Orchestration** | Architectural specification and integration blueprint for 9 specialized CrewAI agents. | **Phase 1** (Done) |
| **Structured Intelligence** | Deconstruct resumes and JDs into validated Pydantic profiles using local Llama 3.2:3b. | **Phase 2** (Done) |
| **Skill Normalization** | Canonical catalog mapping aliases with strict negative boundaries (Java != JS, C != C++ != C#). | **Phase 2** (Done) |
| **Explainable Match Scoring** | 7 weighted dimensions (Coverage, Depth, Relevance, Experience, Education, Keywords). | **Phase 2** (Done) |
| **Project Semantic Relevance** | Local cosine similarity with `nomic-embed-text` correlating projects with target requirements. | **Phase 2** (Done) |
| **Interactive Analysis UI** | Full Next.js 14 dashboard with 7 dimension cards, requirement filters, and local AI telemetry. | **Phase 2** (Done) |
| **Code Evidence Scanning** | Scan local Git repositories and commit logs using GitPython to ground resume claims in real code. | **Phase 3** (Done) |
| **Evidence Grounding UI** | Project registry (`/projects`) and 4-part evidence chain contrast against baseline match score. | **Phase 3** (Done) |
| **CrewAI Multi-Agent Layer** | 5 active CrewAI agents coordinating analysis via deterministic tools and producing dossiers. | **Phase 4** (Done) |
| **Evidence Resume Optimizer** | Iterative rewriting loop (max 3 iters) enhancing technical specificity without inventing claims. | **Phase 5** (Done) |
| **Fact Checker Agent** | Anti-hallucination verification rejecting unsupported skills/metrics and repairing claims. | **Phase 5** (Done) |
| **Deterministic ATS Validator** | Algorithmic parseability, section structure, keyword distribution, and formatting risk scoring. | **Phase 5** (Done) |
| **Immutable Resume Versioning** | Full version history preserving `ORIGINAL` baseline through `FINAL` with diffs and audit trail. | **Phase 5** (Done) |
| **Grounded Interview Prep** | Generate technical deep dives and STAR behavioral questions grounded in real project evidence. | **Phase 6** (Planned) |

---

## 3. Technology Stack

- **Local LLM Engine**: [Ollama](https://ollama.com/) running `llama3.2:3b` (Meta Llama 3.2 3B Parameters)
- **Local Embedding Engine**: Ollama running `nomic-embed-text` (768-dimensional local dense embeddings)
- **Multi-Agent Orchestration**: [CrewAI](https://www.crewai.com/)
- **Backend API**: Python 3.10+ with [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, and Pydantic v2
- **Database & ORM**: SQLite 3 with [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) (Local persistent disk storage)
- **Document Extractors**: [PyMuPDF](https://pymupdf.readthedocs.io/) (`pymupdf`) for PDF, [python-docx](https://python-docx.readthedocs.io/) for DOCX
- **Code Forensic Scanner**: [GitPython](https://gitpython.readthedocs.io/) for local git history and evidence scanning
- **Frontend Dashboard**: [Next.js 14](https://nextjs.org/) (App Router), React 18, [TypeScript](https://www.typescriptlang.org/), and [Tailwind CSS](https://tailwindcss.com/)
- **Icons & Styling**: Lucide React, JetBrains Mono font aesthetic

---

## 4. Architecture Overview

```
                                  [ User Browser ]
                                         │
                                         ▼
                 [ Next.js 14 + TypeScript Productivity Dashboard ]
                                (http://localhost:3000)
                                         │
                                         ▼ REST (Reverse Proxy / Direct)
                     [ FastAPI Application Backend: :8000 ]
                     ┌───────────────────┴───────────────────┐
                     │                                       │
            [ Ingestion Service ]                  [ Database Layer ]
         • PyMuPDF (PDF Parser)                 • SQLite (careercrew.db)
         • python-docx (DOCX)                   • SQLAlchemy 2.0 ORM
         • Path/PII Sanitizer                   • Resumes, JDs, Runs
                     │                                       │
                     ▼                                       ▼
        [ Local Embedding Service ]            [ Local Vector Store ]
     • Ollama /api/embeddings               • ChromaDB Persistent
     • nomic-embed-text (768-dim)           • ./data/embeddings/chroma
                     │                                       │
                     └───────────────────┬───────────────────┘
                                         │
                                         ▼
                   [ CrewAI Multi-Agent Orchestration Layer ]
          ┌──────────────────────────────────────────────────────────┐
          │  Manager Agent (Team Orchestrator)                       │
          │  ├── Stage 1: JD Analyzer + Resume Analyzer + Evidence   │
          │  ├── Stage 2: Match Analyzer (Baseline Fit)              │
          │  ├── Stage 3: Optimization & Verification Loop:          │
          │  │     Optimizer <──> Fact Checker <──> ATS Validator    │
          │  └── Stage 4: Interview Agent (STAR + Technical Prep)   │
          └──────────────────────────────┬───────────────────────────┘
                                         │
                                         ▼
                           [ Local Ollama LLM Service ]
                             http://localhost:11434
                             Model: llama3.2:3b
                         (Zero External Network Calls)
```

---

## 5. Project Monorepo Structure

```
careercrew/
├── backend/
│   ├── app/
│   │   ├── agents/          # 9 specialized CrewAI agents & evidence inspection tools
│   │   ├── api/             # FastAPI v1 endpoints (health, system, ingestion, projects, analysis)
│   │   ├── core/            # Config (Pydantic Settings), logging & privacy filters
│   │   ├── db/              # SQLAlchemy SQLite session, engine, migrations, and init_db
│   │   ├── ingestion/       # PyMuPDF, python-docx, text parsers & security sanitizers
│   │   ├── models/          # SQLAlchemy models (Resume, JobDescription, Project, EvidenceRecord, Run)
│   │   ├── schemas/         # Pydantic validation schemas (Intelligence, Evidence, Projects)
│   │   ├── services/        # Ollama LLM, Embeddings, Chroma, Git Scanner, Detectors, Evidence
│   │   └── main.py          # FastAPI application entrypoint with lifespan events
│   ├── tests/               # 89 automated tests covering Phase 1, 2, and 3
│   ├── pytest.ini           # Pytest asyncio configuration
│   ├── requirements.txt     # Locked local-only dependencies
│   ├── Dockerfile           # Optional backend container
│   └── .env.example         # Environment template
│
├── frontend/
│   ├── app/                 # Next.js 14 App Router pages (Dashboard, Resume, JDs, Projects, etc.)
│   ├── components/          # Serious productivity UI (SystemStatus, Sidebar, Header, Playground)
│   ├── lib/                 # API client wrapper for backend endpoints
│   ├── types/               # TypeScript interfaces
│   ├── tailwind.config.js   # Developer-grade dark palette styling
│   ├── tsconfig.json        # Strict TypeScript configuration
│   ├── Dockerfile           # Optional frontend container
│   └── package.json         # Next.js, React, Tailwind, Lucide dependencies
│
├── data/                    # Persistent local storage (gitignored except .gitkeep)
│   ├── resumes/             # Raw resume documents
│   ├── job_descriptions/    # Target job description files
│   ├── projects/            # Evidence code repositories
│   ├── embeddings/          # Local Chroma vector collections
│   └── database/            # careercrew.db SQLite file
│
├── docs/                    # Production documentation
│   ├── ARCHITECTURE.md      # Detailed system & multi-agent architecture
│   ├── DEVELOPMENT.md       # Setup, test, and operational instructions
│   ├── LOCAL_AI.md          # Local LLM philosophy, air-gap proof, and privacy model
│   └── PHASE_1_REPORT.md    # Detailed Phase 1 implementation & verification report
│
├── scripts/                 # Windows automation scripts
│   ├── start_backend.bat    # Launches FastAPI backend on :8000
│   ├── start_frontend.bat   # Launches Next.js frontend on :3000
│   ├── run_tests.bat        # Runs backend pytest suite
│   └── check_system.bat     # Validates local dependencies & health
│
├── docker-compose.yml       # Optional container orchestration
├── .gitignore               # Strict gitignore protecting personal resumes & binaries
└── README.md                # Project documentation root
```

---

## 6. Quick Start Guide

### Prerequisites
1. **Python 3.10+**: `python --version`
2. **Node.js 18+**: `node --version`
3. **Ollama**: [Download Ollama](https://ollama.com/) and pull the local models:
   ```bash
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```

### 1. Install Backend Dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

### 2. Run Backend Automated Tests
```bash
python -m pytest tests -v
```
*(All 89 tests pass across Phase 1, Phase 2, and Phase 3 against local in-memory SQLite, PyMuPDF, python-docx, Git fixtures, and local Ollama)*

### 3. Start Backend Server
```bash
# From backend directory:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
# Or via Windows script:
..\scripts\start_backend.bat
```
Visit API Documentation: **http://127.0.0.1:8000/docs**  
Verify Health: **http://127.0.0.1:8000/api/health**

### 4. Install & Start Frontend
```bash
cd ../frontend
npm install
npm run dev
# Or via Windows script:
..\scripts\start_frontend.bat
```
Open **http://localhost:3000** in your browser.

---

## 7. Development Roadmap

- [x] **Phase 1: Architecture & Production Foundation**
  - [x] Monorepo structure and directory isolation
  - [x] FastAPI backend with CORS, structured logging, and privacy filters
  - [x] Dedicated Ollama LLM service abstraction with latency logging
  - [x] Local Chroma vector store and local embedding service (`nomic-embed-text`)
  - [x] SQLite database models (Resume, JobDescription, Project, Application, AnalysisRun)
  - [x] PyMuPDF (PDF) & python-docx (DOCX) text extractors with security sanitization
  - [x] CrewAI 9-agent architecture blueprint & pipeline specifications
  - [x] Next.js 14 developer productivity dashboard with real-time hardware telemetry
  - [x] 28/28 automated tests passing
- [x] **Phase 2: Document Intelligence & Explainable Match Engine**
  - [x] Resume Profile structured extraction with Pydantic v2 schemas (`ResumeProfile`)
  - [x] Job Description structured extraction with required/preferred distinction (`JobProfile`)
  - [x] Deterministic Skill Normalizer with strict negative boundaries (`Java != JS`, `C != C++ != C#`)
  - [x] Requirement Classifier with categorization, importance weights, and experience parsing
  - [x] Semantic Project Relevance engine powered by local `nomic-embed-text` embeddings
  - [x] Explainable Matching Engine with 7 weighted dimensions strictly bounded `[0.0 - 100.0]`
  - [x] Synthetic Evaluation Dataset with monotonic candidate ranking (Alice > Bob > Charlie)
  - [x] Next.js 14 Interactive Analysis Dashboard (`/analysis`) with 7 dimension cards & filters
  - [x] SQLite persistence for `AnalysisRun` with full result telemetry
  - [x] 62/62 automated tests passing + Zero cloud API dependency verification
- [x] **Phase 3: Evidence-Grounded Project Intelligence**
  - [x] Local Git repository registration with strict path traversal & system boundary validation
  - [x] Read-only Git scanner with Windows handle safety and sanitized remote URLs
  - [x] Pluggable technology detectors (Python, JavaScript/TypeScript, Docker, Databases, Frontend, Java, AST/Source, Readme)
  - [x] Strict anti-hallucination confidence hierarchy (`VERIFIED` $\ge 0.85$, `LIKELY` $\ge 0.65$, `WEAK` $\le 0.45$, `UNVERIFIED`)
  - [x] 4-part evidence grounding chain (`Job Requirement -> Resume Claim -> Project -> EvidenceRecord`)
  - [x] Deterministic CrewAI EvidenceAgent tool suite (`get_evidence_tools()`)
  - [x] Projects Dashboard (`/projects`) and Match Analysis Evidence Grounding section
  - [x] SQLite schema migrations for `projects` & `evidence_records` table persistence
  - [x] 89/89 automated tests passing + Phase 3 automated verification
- [x] **Phase 4: Local CrewAI Multi-Agent Analysis Orchestration Layer**
  - [x] Activated 5 specialist CrewAI agents (`ManagerAgent`, `JDAnalyzerAgent`, `ResumeAnalyzerAgent`, `EvidenceAgent`, `MatchAnalyzerAgent`)
  - [x] Strictly preserved architectural boundaries for 4 Phase 5 agents (`ResumeOptimizerAgent`, `FactCheckerAgent`, `ATSValidatorAgent`, `InterviewAgent`)
  - [x] Local Ollama LLM binding (`llama3.2:3b`) with zero paid cloud API dependencies
  - [x] Strict role-based tool permission boundaries and runtime access control verification
  - [x] Deterministic agent tools suite for JD analysis, resume parsing, codebase evidence, and match calculation
  - [x] Resilient Pydantic schemas and markdown/trailing comma JSON parser recovery (`parse_agent_json_output`)
  - [x] End-to-end `CrewExecutionService` producing unified `FinalAnalysisDossier`
  - [x] Comparative benchmarking engine (`/api/analysis/benchmark`) contrasting baseline vs multi-agent execution
  - [x] Agent execution telemetry tracking per-agent latency, LLM invocations, and tool invocations
  - [x] Full Next.js 14 frontend integration with triple execution buttons, telemetry panels, and comparative benchmark view
  - [x] 124/124 automated tests passing + 10/10 Phase 4 audit checks passing (100%)
- [x] **Phase 5: Evidence-Grounded Resume Optimization, Fact Checking & ATS Validation**
  - [x] Activated 3 specialist CrewAI agents (`ResumeOptimizerAgent`, `FactCheckerAgent`, `ATSValidatorAgent`)
  - [x] Strictly preserved boundary for deferred `InterviewAgent` (raises `NotImplementedError`)
  - [x] Iterative, bounded optimization loop (`MAX_ITERATIONS = 3`) with non-regression acceptance criteria
  - [x] Deterministic `FactCheckerService`: atomic claim extraction, canonical aliases, technology hierarchy, metric stripping
  - [x] Zero-hallucination guardrail: strict rejection of ungrounded skills (e.g. AWS) and fabricated performance numbers
  - [x] Deterministic `ATSService`: parseability score, section structure, keyword distribution, formatting hazard detection, and mandatory disclaimer
  - [x] Immutable `ResumeVersion` database schema: full lifecycle from `ORIGINAL` (Iteration 0) through `FINAL`
  - [x] REST endpoints: `POST /api/analysis/optimize`, `GET /api/resumes/{id}/versions`, `GET /api/analysis/{id}/audit`
  - [x] Interactive Next.js 14 Optimization UI: score progression tri-cards, anti-hallucination audit panel, ATS diagnostics, version switcher, diff viewer
  - [x] 156/156 automated tests passing + 12/12 Phase 5 verification checks passing (100%)
- [x] **Phase 6: CareerCrew Local Agent + Vercel Dashboard Product Architecture**
  - [x] Packaging and formalization of CareerCrew Local Agent runtime (`/api/local-agent/*`)
  - [x] Standardized health endpoint (`GET /api/local-agent/health`) with zero path/credential exposure
  - [x] Deterministic compatibility diagnostic engine (`GET /api/local-agent/compatibility`) checking 11 system components
  - [x] Feature capabilities negotiation endpoint (`GET /api/local-agent/capabilities`) with honest interview boundary
  - [x] Security invariants: strict localhost binding (`127.0.0.1:8000`), no wildcard CORS (`*` prohibited), read-only Git scanning, zero external cloud AI APIs
  - [x] Persistent Local Agent connection status indicator (`Header.tsx`) across all dashboard views
  - [x] Interactive Onboarding & Setup wizard (`/get-started`) with live diagnostics, re-check button, and OS setup guides
  - [x] Dedicated Privacy Center (`/privacy`) with architecture data flow diagram, data processing matrix, and technical disclosures
  - [x] Enhanced Projects UI (`/projects`) with local repository and GitHub clone connection tabs
  - [x] Vercel deployment architecture documented (`docs/VERCEL_DEPLOYMENT.md`) and verified (12/12 static routes compiled)
  - [x] 173/173 automated backend tests passing + 15/15 Phase 6 verification checks passing (100%)
- [ ] **Phase 7: Grounded Interview Preparation & Job Application Tracking**
  - [ ] Activate `InterviewAgent` for evidence-grounded STAR behavioral questions and technical deep dives
  - [ ] Implement Job Application lifecycle tracking (`/applications`)
  - [ ] Export optimized resumes to PDF and DOCX formats

---

## 8. License

MIT License. Designed and engineered for privacy-conscious software engineers.
