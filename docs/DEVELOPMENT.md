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



