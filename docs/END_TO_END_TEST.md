# CareerCrew — End-to-End Production Acceptance & Verification Guide

This document provides a comprehensive 16-section walkthrough verifying the complete CareerCrew product lifecycle from a fresh user install to multi-agent optimization, fact-checked claim verification, and ATS compatibility scoring.

---

## 1. System Prerequisites

Before launching CareerCrew, ensure the local workstation satisfies the following software dependencies:

- **Operating System**: Windows 10/11, macOS, or Linux (x86_64 or arm64).
- **Python**: Python 3.10 or 3.11 with `pip` and virtual environment support.
- **Node.js**: Node.js 18.x or 20.x with `npm`.
- **Git**: Git CLI installed and available in `PATH`.
- **Ollama**: Local Ollama runtime installed (`https://ollama.ai`).
  - Model 1: `llama3.2:3b` (text generation & structured extraction).
  - Model 2: `nomic-embed-text` (local vector embeddings).

---

## 2. Repository Cloning & Fresh Working State

Clone the canonical repository and verify Git state:

```bash
git clone https://github.com/gowthxm07/Resume_Matcher_Local_Agent.git careercrew
cd careercrew
git status
```

Verify that no third-party cloud API credentials (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `COHERE_API_KEY`) exist in the environment or `.env` files.

---

## 3. Environment Configuration & Privacy Invariants

CareerCrew operates under strict zero-cloud privacy invariants:

```env
# Backend Environment (.env or defaults)
PROJECT_NAME=CareerCrew
ENVIRONMENT=production
HOST=127.0.0.1
PORT=8000
DEBUG=false

# Local LLM & Embeddings (Strictly Localhost)
OLLAMA_BASE_URL=http://127.0.0.1:11434
DEFAULT_LLM_MODEL=llama3.2:3b
EMBEDDING_MODEL=nomic-embed-text

# Local Storage (Local Filesystem Only)
DATABASE_URL=sqlite:///data/database/careercrew.db
VECTOR_STORE_DIR=data/embeddings/chroma

# Prohibited Cloud Endpoints
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

---

## 4. Starting the Local Agent

### Option A: One-Click Windows Launchers
CareerCrew provides automated launchers that perform initial dependency sanity checks before binding the server:
- Command Prompt: `start_careercrew.bat`
- PowerShell: `.\start_careercrew.ps1`

### Option B: Manual Virtualenv Launch
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Verify agent reachability:
```bash
curl http://127.0.0.1:8000/api/local-agent/health
```
Expected output:
```json
{
  "agent": "careercrew-local-agent",
  "status": "ready",
  "version": "1.0.0",
  "api_version": "1",
  "local_only": true
}
```

---

## 5. Starting the Frontend Dashboard

In a separate terminal:
```powershell
cd frontend
npm install
npm run dev
```
The dashboard will be available at `http://localhost:3000`.

---

## 6. Compatibility Check & Setup Wizard

1. Open `http://localhost:3000/get-started` in your browser.
2. The Setup Wizard automatically issues `GET http://127.0.0.1:8000/api/local-agent/compatibility`.
3. The response provides deterministic checks across 10 system dimensions:
   - Python runtime
   - FastAPI backend
   - CrewAI orchestrator (`1.15.23`)
   - Ollama service reachability
   - `llama3.2:3b` model weights
   - `nomic-embed-text` embedding model
   - Git CLI installation
   - SQLite database writeability
   - ChromaDB local vector storage
   - Localhost port 8000 binding

---

## 7. Fresh User Failure Simulation & Live Recovery

To verify that the system gracefully handles setup errors:
1. **Simulation**: Stop Ollama (`taskkill /F /IM ollama.exe` or close Ollama app).
2. Refresh `http://localhost:3000/get-started`.
3. **Observation**: Ollama component displays `MISSING` with an actionable command prompt: `ollama run llama3.2:3b`.
4. **Recovery**: Start Ollama in the background (`ollama serve`).
5. Click **Re-run Diagnostics** on the Setup Wizard.
6. **Result**: Status changes to `READY` immediately without requiring a backend restart.

---

## 8. Repository Registration & Evidence Scanning

Connect a candidate software project for evidence extraction:
1. Navigate to `/projects`.
2. Register a local project directory:
   - Name: `Python FastAPI Backend`
   - Path: `backend/tests/fixtures/repos/python_fastapi_backend`
3. Click **Scan Repository**.
4. The Git scanner executes locally:
   - Scans repository trees and commits safely without invoking arbitrary shell commands.
   - Parses AST and dependency descriptors (`requirements.txt`, `pyproject.toml`, `package.json`).
   - Indexes canonical technologies: `python`, `fastapi`, `postgresql`, `docker`, `git`.

---

## 9. Evidence Verification & Confidence Levels

Navigate to the project evidence dossier to verify classification:
- **`VERIFIED` (Confidence $\ge 0.90$)**: Technologies corroborated by package manifests, import trees, or direct code usage.
- **`PARTIALLY_VERIFIED` (Confidence $0.60 - 0.89$)**: Technologies mentioned in documentation or commit messages without direct import statements.
- **`UNVERIFIED` (Confidence $< 0.60$)**: Technologies claimed in documentation but uncorroborated by source code.

---

## 10. Resume Ingestion & Parsing

1. Navigate to `/resume`.
2. Upload a candidate resume (PDF, DOCX, or TXT) or paste raw text.
3. The parser executes `DocumentParser.parse_bytes()` deterministically.
4. Structured entities are extracted:
   - Contact info (email, GitHub, LinkedIn).
   - Skills inventory (categorized by language, framework, database, tool).
   - Work experience items.
   - Projects and academic credentials.
5. Ingestion hashes the document with SHA-256 and persists it to `careercrew.db`.

---

## 11. Job Description Ingestion & Classification

1. Navigate to `/job-descriptions` or paste the target job description into the analysis interface.
2. The `RequirementClassifier` partitions job requirements into:
   - **Required Skills**: Non-negotiable core competencies.
   - **Preferred Skills**: Bonus or nice-to-have qualifications.
   - **Years of Experience**: Seniority indicators.
   - **Domain Context**: Industry-specific keywords.

---

## 12. Baseline Analysis & Explainable Match Score

Execute `POST /api/analysis/match`:
1. The deterministic `MatchingEngine` computes a multi-dimensional score bounded in $[0.0, 100.0]$:
   - **Required Skill Match** ($40\%$ weight).
   - **Preferred Skill Match** ($15\%$ weight).
   - **Experience Match** ($20\%$ weight).
   - **Project Evidence Relevance** ($15\%$ weight).
   - **Semantic Similarity** ($10\%$ weight).
2. The result categorizes every requirement as `MATCH`, `PARTIAL_MATCH`, or `MISSING`.
3. The analysis is persisted to SQLite with a unique `analysis_run_id`.

---

## 13. Multi-Agent Analysis Layer

Execute `POST /api/crew/analyze`:
1. CrewAI multi-agent crew orchestrates specialized agents:
   - `ResumeIntelligenceAgent`: Analyzes profile strengths and presentation quality.
   - `JobIntelligenceAgent`: Decodes hidden hiring manager intent.
   - `ProjectEvidenceAgent`: Corroborates resume bullet points against repository evidence records.
   - `MatchingOrchestratorAgent`: Synthesizes final recommendations.
2. Agents strictly execute local tools (`retrieve_evidence`, `verify_skill`, `query_chroma`).
3. Note: `InterviewAgent` is strictly deferred (`interview_intelligence: false`).

---

## 14. Evidence-Grounded Resume Optimization

Execute `POST /api/analysis/optimize`:
1. The optimization loop analyzes missing required keywords and weak bullet points.
2. Proposals are generated according to strict change types:
   - `TECHNICAL_SPECIFICITY`: Anchoring vague achievements to verified technologies.
   - `KEYWORD_ALIGNMENT`: Using canonical phrasing present in the JD.
   - `ACHIEVEMENT_FRAMING`: Enhancing clarity without fabricating metrics.
3. If no projects are registered or no additional evidence exists, the optimizer halts safely without making up claims.

---

## 15. Fact Checking & Zero-Hallucination Guardrail

Every proposed change passes through `FactCheckerService.verify_change()`:
- **Rule A**: Present in original bullet $\to$ `SUPPORTED`.
- **Rule B**: Present in existing resume sections $\to$ `SUPPORTED`.
- **Rule C**: Verified in registered repository technologies $\to$ `SUPPORTED`.
- **Rule D / E**: Unverified technologies, fabricated metrics, or superlative claims $\to$ `UNSUPPORTED`.
- Any proposal containing ungrounded claims (e.g., inventing AWS, Kubernetes, or fabricated 10x throughput scaling) is strictly rejected or deterministically repaired.

---

## 16. ATS Validation, Versioning, and Audit Trails

1. **ATS Evaluation**:
   - `ATSService.evaluate_resume()` assesses parseability, section structure, keyword density, and formatting risks.
   - Returns heuristic `overall_ats_score` and displays mandatory heuristic disclaimer:
     > *"ATS scores are heuristic estimates of machine parseability and keyword alignment, not guarantees of employer ATS platform outcomes."*
2. **Resume Versioning**:
   - Snapshot 0 is preserved as `ORIGINAL`.
   - Iteration snapshots are recorded as `CANDIDATE`.
   - Highest-scoring validated version is tagged `FINAL`.
3. **Audit Trail**:
   - Every modification, claim validation, ATS evaluation, and user decision is recorded in `ResumeVersion.audit_trail` with UTC timestamps and SHA-256 checksums.
