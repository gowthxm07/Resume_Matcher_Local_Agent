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

### 9.3 Running All Unit & Integration Tests (89 Tests)
Run the entire backend test suite across Phase 1, Phase 2, and Phase 3:
```bash
cd backend
python -m pytest tests -v
```
All 89 tests pass:
- **Phase 1**: Health, Ingestion, Database, Ollama Service, Agent Blueprint (28 tests)
- **Phase 2**: Intelligence Schemas, Skill Normalizer, Requirement Classifier, Extractor, Project Relevance, Matching Engine, Evaluation Dataset (34 tests)
- **Phase 3**: Path Validator, Safe Git Scanner, Technology Detectors, Evidence Service, Projects API (27 tests)

### 9.4 Automated Phase 3 Verification
Execute the automated Phase 3 verification script:
```bash
python scripts/verify_phase3.py
```
This script verifies:
1. Local Ollama & zero cloud API constraint.
2. Path security validator (blocks root, system dirs, data dirs, path traversal).
3. Safe Git scanner (metadata, sanitized remotes, non-git fallback).
4. Modular technology detectors (Python, Package.json, Docker/Compose, Source code, Readme).
5. Evidence service & confidence hierarchy (`VERIFIED` $\ge 0.85$, `LIKELY` $\ge 0.65$, `WEAK` $\le 0.45$, `UNVERIFIED`).
6. 4-part evidence chain construction & project registration.
7. CrewAI EvidenceAgent tools (`get_evidence_tools()`).


