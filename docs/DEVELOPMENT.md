# CareerCrew Development Guide

This guide details instructions for developing, testing, and verifying CareerCrew locally on Windows, macOS, or Linux.

---

## 1. Prerequisites

Ensure the following tools are installed on your host system:

- **Python 3.10+**: `python --version`
- **Node.js 18+ (Node 20+ Recommended)**: `node --version`
- **Ollama**: [https://ollama.com/](https://ollama.com/)
- **Git**: `git --version`

---

## 2. Setting Up Ollama (Local LLM & Embeddings)

1. Start the Ollama background service if it is not already running:
   ```bash
   ollama serve
   ```
2. Pull the required models:
   ```bash
   # Primary local LLM (approx 2.0 GB)
   ollama pull llama3.2:3b

   # Primary local embedding model (approx 274 MB)
   ollama pull nomic-embed-text
   ```
3. Verify models are present:
   ```bash
   ollama list
   ```

---

## 3. Backend Setup

### Installation
Navigate to `backend` directory and install dependencies:
```bash
cd backend
python -m pip install -r requirements.txt
```

### Environment Configuration
Copy `.env.example` to `.env`:
```bash
copy .env.example .env   # Windows
# or
cp .env.example .env     # Linux / macOS
```

### Running Backend Server
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Or run the helper script on Windows:
```cmd
scripts\start_backend.bat
```

The backend is accessible at:
- **API Base**: `http://127.0.0.1:8000/api`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Alternative ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 4. Frontend Setup

### Installation
Navigate to `frontend` directory:
```bash
cd frontend
npm install
```

### Starting Frontend Development Server
```bash
npm run dev
```
Or run the helper script on Windows:
```cmd
scripts\start_frontend.bat
```
Open **http://localhost:3000** in your browser.

### Building & Checking Frontend
```bash
# Typecheck TypeScript without emitting JS:
npm run typecheck

# Production build:
npm run build
```

---

## 5. Automated Testing

Run the full pytest backend test suite from `backend/`:
```bash
cd backend
python -m pytest tests -v
```
Or run the helper script:
```cmd
scripts\run_tests.bat
```

To run a specific test file:
```bash
python -m pytest tests/test_health.py -v
python -m pytest tests/test_ingestion.py -v
python -m pytest tests/test_ollama_service.py -v
```

---

## 6. Verifying System Health Endpoints

Use `curl` or PowerShell to introspect health:

### Basic Health Check
```bash
curl http://127.0.0.1:8000/api/health
```
Expected output:
```json
{
  "status": "ok",
  "service": "careercrew-backend",
  "version": "0.1.0",
  "timestamp": "2026-10-05T15:30:00Z"
}
```

### Comprehensive Host Telemetry
```bash
curl http://127.0.0.1:8000/api/system/status
```
Expected output reports:
- Backend status: `ok`
- Ollama reachability: `true`, configured model: `llama3.2:3b`
- Database: `connected`, engine: `sqlite`, tables: `["resumes", "job_descriptions", "projects", "applications", "analysis_runs"]`
- Vector store: `healthy`, engine: `chroma`, path: `./data/embeddings/chroma`
- `local_only_verified`: `true`

### Test Local Inference
```bash
curl -X POST http://127.0.0.1:8000/api/ollama/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello in 3 words."}'
```

---

## 7. Optional Docker Deployment

If you prefer to run within Docker:
```bash
docker-compose up --build
```
*Note: Docker is completely optional. Direct execution on your host OS is supported and recommended for local GPU acceleration.*

---

## 8. Phase 2 Verification & Match Testing

### Automated Phase 2 Verification
Run the complete Phase 2 verification script:
```bash
python scripts/verify_phase2.py
```
This script tests:
1. Local Ollama & zero cloud API constraint.
2. Skill normalizer & strict negative boundaries.
3. Requirement classifier & experience parsing.
4. Extractor service hashing & deterministic fallback.
5. Project semantic relevance (cosine similarity & lexical overlap).
6. Explainable matching engine (7 dimensions, sum of weights = 1.0).
7. Synthetic evaluation dataset ranking consistency (Alice > Bob > Charlie).
8. SQLite persistence of `AnalysisRun`.

### Running All Unit & Integration Tests
```bash
cd backend
python -m pytest tests -v
```
All 62 tests across Phase 1 and Phase 2 will execute and pass.

### Interactive Analysis API Testing
Execute a match analysis directly via `curl` or PowerShell:
```bash
curl -X POST http://127.0.0.1:8000/api/analysis/match \
  -F "resume_text=Senior Python Engineer with 5+ years experience in FastAPI and PostgreSQL." \
  -F "jd_text=Looking for a Senior Python Developer with FastAPI and PostgreSQL experience."
```

---

## 9. Phase 3: Project Evidence & Verification Testing

### 9.1 Registering and Scanning Projects
Register a local candidate repository via API:
```bash
curl -X POST http://127.0.0.1:8000/api/projects/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Backend Service", "path": "D:\\Projects\\BackendService"}'
```

Scan the repository for evidence:
```bash
curl -X POST http://127.0.0.1:8000/api/projects/1/scan
```

Query indexed evidence records:
```bash
curl http://127.0.0.1:8000/api/projects/1/evidence
```

### 9.2 Verifying Candidate Skills
Verify a list of technical skills against registered projects:
```bash
curl -X POST http://127.0.0.1:8000/api/projects/verify-skills \
  -H "Content-Type: application/json" \
  -d '{"skills": ["FastAPI", "PostgreSQL", "Docker", "Kubernetes"]}'
```

### 9.3 Running All Unit & Integration Tests (124 Tests)
Run the entire backend test suite across all completed phases:
```bash
cd backend
python -m pytest tests -v
```
All 124 tests pass:
- **Phase 1**: Health, Ingestion, Database, Ollama Service, Agent Blueprint (28 tests)
- **Phase 2**: Intelligence Schemas, Skill Normalizer, Requirement Classifier, Extractor, Project Relevance, Matching Engine, Evaluation Dataset (34 tests)
- **Phase 3**: Path Validator, Safe Git Scanner, Technology Detectors, Evidence Service, Projects API (27 tests)
- **Phase 4**: Agent Tool Permissions, Agent Schemas & Dossier, Crew Execution Service, Crew API Endpoints, Monotonic Synthetic Ranking (35 tests)

### 9.4 Automated Phase 3 Verification
Execute the automated Phase 3 verification script:
```bash
python scripts/verify_phase3.py
```

---

## 10. Phase 4: Multi-Agent Orchestration & Benchmarking

### 10.1 Running CrewAI Multi-Agent Analysis via API
Execute end-to-end multi-agent orchestration:
```bash
curl -X POST http://127.0.0.1:8000/api/analysis/crew \
  -H "Content-Type: application/json" \
  -d '{
    "raw_resume_text": "Alex Chen, Senior Software Engineer with Python, FastAPI, Docker, and PostgreSQL experience.",
    "raw_jd_text": "Senior Python Engineer requiring 5+ years experience with FastAPI, PostgreSQL, and Docker.",
    "project_ids": [],
    "use_live_llm": false
  }'
```

### 10.2 Comparative Benchmark Mode
Contrasts deterministic baseline vs multi-agent execution on identical inputs:
```bash
curl -X POST http://127.0.0.1:8000/api/analysis/benchmark \
  -H "Content-Type: application/json" \
  -d '{
    "raw_resume_text": "Alex Chen, Senior Software Engineer with Python and FastAPI.",
    "raw_jd_text": "Senior Python Engineer requiring FastAPI and PostgreSQL.",
    "project_ids": []
  }'
```

### 10.3 Retrieving Stored Analysis Dossiers
Retrieve an audit-traceable dossier by ID:
```bash
curl http://127.0.0.1:8000/api/analysis/{analysis_id}/dossier
```

### 10.4 Automated Phase 4 Verification Suite
Execute the Phase 4 verification script covering all 10 criteria:
```bash
python scripts/verify_phase4.py
```
This script audits:
1. Local model (`llama3.2:3b`) and embedding (`nomic-embed-text`) configuration.
2. 9-agent architecture (5 active Phase 4 agents, 4 strictly deferred Phase 5 agents).
3. Strict role-based tool permissions (least-privilege runtime access control).
4. CrewAI agent creation and local Ollama endpoint binding.
5. Structured Pydantic schemas and markdown/trailing comma JSON recovery.
6. Deterministic application tools execution.
7. Agent execution telemetry and duration recording.
8. Evidence grounding and zero hallucination with 0 registered projects.
9. Baseline vs multi-agent comparative benchmark execution.
10. Privacy constraints and zero cloud API keys/endpoints audit.

### 10.5 Frontend Validation
Run typecheck and production build:
```bash
cd frontend
npm run typecheck
npm run build
```

---

## 11. Phase 5: Resume Optimization, Fact Checking & ATS Validation Testing

### 11.1 Running Resume Optimization via API
Execute end-to-end evidence-grounded optimization:
```bash
curl -X POST http://127.0.0.1:8000/api/analysis/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "raw_resume_text": "Alex Chen\nSenior Backend Engineer\nPython, FastAPI, and Docker experience.",
    "raw_jd_text": "Senior Backend Engineer requiring Python, FastAPI, Docker, and PostgreSQL.",
    "project_ids": [],
    "max_iterations": 3,
    "use_live_llm": false
  }'
```

### 11.2 Inspecting Resume Versions & Audit Trail
Query immutable resume versions:
```bash
curl http://127.0.0.1:8000/api/resumes/{resume_id}/versions
```

Retrieve detailed audit trail for an optimization run:
```bash
curl http://127.0.0.1:8000/api/analysis/{analysis_id}/audit
```

### 11.3 Running Phase 5 Test Suites (32 Tests)
Run only the Phase 5 test suites:
```bash
cd backend
python -m pytest tests/test_resume_optimizer_agent.py tests/test_fact_checker_agent.py tests/test_ats_validator_agent.py tests/test_optimization_loop.py tests/test_phase5_synthetic.py tests/test_phase5_security_permissions.py tests/test_optimization_api.py -v
```

### 11.4 Complete Regression Test Suite (156 Tests)
Run the entire backend test suite:
```bash
cd backend
python -m pytest tests -q
```
All 156 tests pass across Phase 1 through Phase 5.

### 11.5 Automated Phase 5 Verification
Run the 12-point automated verification script:
```bash
python scripts/verify_phase5.py
```
This script audits:
1. Local-Only Privacy & Zero Cloud Dependency Audit
2. 9-Agent Architecture & Phase 5 Activation State
3. Strict Agent Tool Permissions & Role Access Control Boundaries
4. Deterministic ATS Validation Engine & Heuristic Disclaimer
5. Deterministic Fact-Checking Service (Atomic claims, canonicalization, metric repair)
6. Anti-Hallucination Guardrails (Strict rejection of ungrounded skills and metrics)
7. Immutable Resume Versioning (ORIGINAL baseline preserved, FINAL designated)
8. Bounded Iterative Optimization Loop (Max 3 iterations, regression prevention)
9. Synthetic Scenario A (High-evidence candidate: verified improvements)
10. Synthetic Scenario B (Skill gap: missing required skills NOT manufactured)
11. Synthetic Scenario C (Inflated claims: unverified metrics stripped/repaired)
12. Comprehensive Audit Trail & Persisted Analysis Run

---

## 12. Phase 6: Local Agent + Vercel Dashboard Verification & Endpoints

### 12.1 Local Agent Endpoints

```bash
# 1. Health & Liveness
curl http://127.0.0.1:8000/api/local-agent/health

# 2. Deterministic Compatibility Diagnostics
curl http://127.0.0.1:8000/api/local-agent/compatibility

# 3. Active Capabilities Negotiation
curl http://127.0.0.1:8000/api/local-agent/capabilities
```

### 12.2 Running Local Agent & Tests

```bash
# Start Local Agent
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Run all 173 backend tests
pytest backend/tests

# Run Phase 6 Local Agent test suite
pytest backend/tests/test_local_agent.py -v

# Run 15-point automated Phase 6 verification
python scripts/verify_phase6.py

# Frontend typecheck & production build
cd frontend
npm run typecheck
npm run build
```

---

## 13. Phase 7: Production Validation, End-to-End Acceptance & Fresh-User Readiness

### 13.1 One-Click Launchers
CareerCrew provides cross-platform launch scripts:
- Windows Command Prompt: `start_careercrew.bat`
- Windows PowerShell: `.\start_careercrew.ps1`

### 13.2 Running Phase 7 Test Suite & Verification Audit
```bash
# 1. Run Phase 7 End-to-End Acceptance Tests
pytest backend/tests/test_phase7_e2e_acceptance.py -v

# 2. Run full 180-test regression suite
pytest backend/tests -q

# 3. Run 22-point automated Phase 7 verification audit
python scripts/verify_phase7.py

# 4. Frontend verification
cd frontend
npm run typecheck
npm run build
```

### 13.3 Acceptance Artifacts
- Developer Walkthrough: `docs/END_TO_END_TEST.md`
- Candidate User Guide: `docs/USER_GUIDE.md`
- Live Demonstration Script: `docs/DEMO_SCRIPT.md`
- Milestone Report: `docs/PHASE_7_REPORT.md`



