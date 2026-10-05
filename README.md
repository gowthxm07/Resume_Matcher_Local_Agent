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
| **Code Evidence Scanning** | Scan local Git repositories and commit logs using GitPython to ground resume claims in real code. | **Phase 3** (Planned) |
| **Zero-Hallucination Loop** | Iterative feedback loop between Resume Optimizer and Fact Checker to rewrite resumes. | **Phase 3** (Planned) |
| **ATS Emulation & Scoring** | Emulate enterprise ATS parsers (Taleo, Greenhouse, Workday) for structure and keyword density. | **Phase 3** (Planned) |
| **Grounded Interview Prep** | Generate technical deep dives and STAR behavioral questions grounded in real project evidence. | **Phase 3** (Planned) |

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
│   │   ├── agents/          # 9 specialized CrewAI agent specifications & orchestrator
│   │   ├── api/             # FastAPI v1 endpoints (health, system, ingestion, agents, db)
│   │   ├── core/            # Config (Pydantic Settings), logging & privacy filters
│   │   ├── db/              # SQLAlchemy SQLite session, engine, and init_db
│   │   ├── ingestion/       # PyMuPDF, python-docx, text parsers & security sanitizers
│   │   ├── models/          # SQLAlchemy models (Resume, JobDescription, Project, Application, Run)
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Ollama LLM service, Embedding service, Chroma vector store
│   │   └── main.py          # FastAPI application entrypoint with lifespan events
│   ├── tests/               # 28 automated tests covering health, db, ingestion, ollama
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
*(All 28 tests pass against local in-memory SQLite, PyMuPDF, python-docx, and local Ollama)*

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
- [ ] **Phase 3: Multi-Agent Optimization & Evidence Verification**
  - [ ] Implement Git commit & code pattern forensic scanner using GitPython
  - [ ] Implement iterative Resume Optimizer <-> Fact Checker zero-hallucination loop
  - [ ] Implement ATS Validator emulation for major enterprise systems (Taleo, Greenhouse)
  - [ ] Implement Grounded Interview Preparation generator (STAR format + technical deep dives)
  - [ ] Export optimized resumes to PDF and DOCX formats

---

## 8. License

MIT License. Designed and engineered for privacy-conscious software engineers.
