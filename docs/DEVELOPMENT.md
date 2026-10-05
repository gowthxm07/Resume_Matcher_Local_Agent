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
