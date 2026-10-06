# CareerCrew Local Agent Runtime Guide

**Version**: `1.0.0`  
**Protocol API**: `v1`  
**Default Host Binding**: `127.0.0.1:8000`  
**License**: MIT / Proprietary Open Core  

---

## 1. Overview & Architectural Role

The **CareerCrew Local Agent** is the core privacy engine of CareerCrew. It runs entirely on the candidate's personal computer or private workstation, providing a local HTTP REST interface for the CareerCrew dashboard (whether accessed locally or via a Vercel-hosted web UI).

```text
┌────────────────────────────────────────────────────────┐
│             Vercel-Hosted Web Dashboard                │
│              (Next.js 14 Presentation)                 │
└───────────────────────────┬────────────────────────────┘
                            │
               Strict Localhost HTTP
               (http://127.0.0.1:8000)
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 CAREERCREW LOCAL AGENT                 │
│                                                        │
│  • FastAPI REST Server (127.0.0.1:8000)                │
│  • Compatibility Engine (Deterministic Diagnostics)    │
│  • Multi-Agent CrewAI Orchestration Layer             │
│  • Ollama Llama 3.2:3b Local LLM Inference             │
│  • Ollama nomic-embed-text Local Vector Embeddings     │
│  • SQLite Relational Database Engine                   │
│  • ChromaDB Local Vector Store                         │
│  • Read-Only Local Git Repository Scanner              │
│  • Deterministic Fact-Checker & ATS Engine             │
└────────────────────────────────────────────────────────┘
```

---

## 2. Local Agent API Endpoints

The Local Agent exposes a dedicated namespace under `/api/local-agent/*`:

### A. Health & Liveness
```http
GET /api/local-agent/health
```
**Response**:
```json
{
  "agent": "careercrew-local-agent",
  "status": "ready",
  "version": "1.0.0",
  "api_version": "1",
  "local_only": true
}
```
*Guarantees: Zero filesystem paths, credentials, tokens, or environment secrets are exposed.*

### B. Deterministic System Compatibility Diagnostics
```http
GET /api/local-agent/compatibility
```
Executes non-destructive, deterministic checks against all local subsystems.

**Response**:
```json
{
  "ready": true,
  "checks": [
    {
      "name": "CareerCrew Local Agent",
      "status": "READY",
      "required": true,
      "detected_version": "1.0.0",
      "required_version": "1.0.0",
      "message": "CareerCrew Local Agent runtime active on localhost.",
      "setup_route": "/get-started"
    },
    {
      "name": "Ollama",
      "status": "READY",
      "required": true,
      "detected_version": "reachable",
      "required_version": ">= 0.1.0",
      "message": "Local Ollama server is running and reachable on localhost.",
      "setup_route": "/get-started#ollama"
    },
    {
      "name": "Llama 3.2:3B",
      "status": "READY",
      "required": true,
      "detected_version": "llama3.2:3b",
      "required_version": "llama3.2:3b",
      "message": "Llama 3.2:3b inference model is installed and ready in local Ollama.",
      "setup_route": "/get-started#models"
    },
    {
      "name": "nomic-embed-text",
      "status": "READY",
      "required": true,
      "detected_version": "nomic-embed-text:latest",
      "required_version": "nomic-embed-text",
      "message": "Local embedding model 'nomic-embed-text' is installed in Ollama.",
      "setup_route": "/get-started#models"
    },
    {
      "name": "CrewAI",
      "status": "READY",
      "required": true,
      "detected_version": "1.15.23",
      "required_version": ">= 0.50.0",
      "message": "CrewAI multi-agent orchestration runtime is ready.",
      "setup_route": "/get-started#crewai"
    },
    {
      "name": "FastAPI",
      "status": "READY",
      "required": true,
      "detected_version": "0.115.11",
      "required_version": ">= 0.100.0",
      "message": "FastAPI local REST server is active.",
      "setup_route": "/get-started#fastapi"
    },
    {
      "name": "Git",
      "status": "READY",
      "required": true,
      "detected_version": "2.52.0.windows.1",
      "required_version": ">= 2.20",
      "message": "Git CLI detected. Evidence scanning runtime ready.",
      "setup_route": "/get-started#git"
    },
    {
      "name": "SQLite",
      "status": "READY",
      "required": true,
      "detected_version": "3.40.1",
      "required_version": ">= 3.30",
      "message": "SQLite 3.40.1 local relational database operational.",
      "setup_route": "/get-started#sqlite"
    },
    {
      "name": "ChromaDB",
      "status": "READY",
      "required": true,
      "detected_version": "1.1.1",
      "required_version": ">= 0.4.0",
      "message": "ChromaDB local vector store persistence accessible.",
      "setup_route": "/get-started#chroma"
    },
    {
      "name": "Python",
      "status": "READY",
      "required": true,
      "detected_version": "3.10.11",
      "required_version": ">= 3.10",
      "message": "Python 3.10.11 runtime is fully supported.",
      "setup_route": "/get-started#python"
    },
    {
      "name": "Local Ports",
      "status": "READY",
      "required": false,
      "detected_version": "Port 8000 (API), 11434 (Ollama)",
      "required_version": "8000, 11434",
      "message": "Local Agent bound to 127.0.0.1:8000; Ollama configured at http://localhost:11434.",
      "setup_route": "/get-started#ports"
    }
  ],
  "agent_version": "1.0.0",
  "timestamp": "2026-10-06T04:35:40.123456Z"
}
```

### C. Active Capabilities Negotiation
```http
GET /api/local-agent/capabilities
```
**Response**:
```json
{
  "analysis": true,
  "multi_agent": true,
  "evidence_scanning": true,
  "resume_optimization": true,
  "fact_checking": true,
  "ats_validation": true,
  "github_import": true,
  "interview_intelligence": false
}
```
*Note: `interview_intelligence` is strictly `false` (deferred per Phase 5/6 boundary).*

---

## 3. Starting the Local Agent

### Prerequisites
1. Python 3.10+
2. Ollama running locally (`ollama serve`)
3. Models pulled:
   ```bash
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```

### Execution Command
From the project root:
```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 4. Security & Isolation Controls

| Security Control | Implementation Mechanism |
| :--- | :--- |
| **Localhost-Only Binding** | `HOST = "127.0.0.1"` enforced by default. Rejects public network interfaces. |
| **No Wildcard CORS** | `Settings` validator strictly raises `ValueError` if `*` is present in `CORS_ORIGINS`. |
| **Read-Only Git Scans** | Git engine operates strictly via non-destructive AST and read-only tree inspections. |
| **Air-Gapped Operation** | Once models and Python wheels are installed, the Local Agent requires **zero internet access**. |
| **Prohibited Cloud APIs** | `field_validator` rejects any configuration setting pointing to OpenAI, Anthropic, Gemini, Bedrock, or Azure. |
