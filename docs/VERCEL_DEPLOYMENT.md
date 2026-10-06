# CareerCrew — Vercel Dashboard Deployment Guide

**Architecture Model**: Hybrid Cloud UI + Local Agent Intelligence  
**Cloud Layer**: Next.js 14 Static / Client Frontend (Vercel)  
**Private Layer**: CareerCrew Local Agent (`127.0.0.1:8000`)  

---

## 1. Architectural Philosophy

CareerCrew is intentionally designed with a **privacy-first separation of concerns**:

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
│  • FastAPI Local REST Server                           │
│  • Ollama Llama 3.2:3b Local LLM Inference             │
│  • Ollama nomic-embed-text Embeddings                  │
│  • CrewAI Multi-Agent Orchestration Layer              │
│  • Local SQLite Database & ChromaDB Vector Store       │
│  • Read-Only Local Git Repository Evidence Engine      │
└────────────────────────────────────────────────────────┘
```

### What is Deployed to Vercel
- **User Interface Only**: Next.js 14 frontend pages (`/`, `/get-started`, `/privacy`, `/projects`, `/analysis`, `/resume`, `/job-descriptions`, `/settings`).
- Static styling, Tailwind components, and client-side JavaScript.
- **ZERO candidate data, ZERO resumes, ZERO code repositories, ZERO vector databases, and ZERO AI inference engines are deployed to Vercel.**

### What Remains on Your Local Machine
- Resume PDFs and DOCX files.
- Job descriptions and vacancy listings.
- Local software repositories and Git commit histories.
- SQLite database tables (`careercrew.db`).
- ChromaDB vector collections and embeddings.
- Ollama runtime and LLM model weights (`llama3.2:3b`, `nomic-embed-text`).
- CrewAI agent orchestration traces and telemetry.

---

## 2. Environment Variables & Configuration

When deploying the frontend to Vercel, configure the following environment variable in the Vercel Project Settings:

| Variable | Recommended Value | Purpose |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000/api` | Directs the browser's client-side API client to communicate with the local agent runtime. |

### Build Safety
The Next.js build does **not** require an active connection to `127.0.0.1:8000` during compilation. All pages use runtime client-side data fetching with graceful offline error boundaries (`Local Agent Offline` banners and empty states).

---

## 3. Local Agent CORS Configuration

To allow the Vercel-hosted dashboard to communicate with your local machine, the Local Agent must include your Vercel deployment domain in its allowed CORS origins:

In your local `.env` or `backend/.env`:
```ini
# Add your production or preview Vercel domain:
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://careercrew.vercel.app
```

> **Security Rule**: CareerCrew strictly rejects `CORS_ORIGINS=["*"]`. Wildcard CORS is prohibited by Pydantic configuration validators to prevent unauthorized third-party websites from probing your local agent.

---

## 4. Browser Security & Localhost Loopback Access

Modern web browsers enforce specific security policies when an `https://` website communicates with an `http://` localhost address:

### A. Potentially Trustworthy Origin (Loopback)
According to the W3C Secure Contexts specification and RFC 6761, major browsers (Google Chrome, Microsoft Edge, Mozilla Firefox) recognize `http://127.0.0.1` and `http://localhost` as "potentially trustworthy origins". This allows secure HTTPS web apps (such as Docker Desktop Web UI, Ledger Live, and CareerCrew) to interface with local daemons.

### B. Private Network Access (PNA)
Chromium browsers are gradually rolling out Private Network Access (PNA) preflights. CareerCrew local agent supports standard preflight `OPTIONS` requests.

### C. Troubleshooting Loopback Restrictions
If your browser or corporate security software blocks public HTTPS pages from calling `http://127.0.0.1`:
1. **Disable strict shield/ad-blocker** for your CareerCrew Vercel domain.
2. **Local Dashboard Alternative**: Run the frontend locally alongside the agent:
   ```bash
   cd frontend
   npm run dev
   ```
   Open `http://localhost:3000`. In this mode, both frontend and agent reside on localhost, eliminating cross-origin restrictions entirely.

---

## 5. Step-by-Step Vercel Deployment

1. **Push Code to GitHub**:
   Ensure all changes are pushed to `main` in `gowthxm07/Resume_Matcher_Local_Agent`.
2. **Import Repository in Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/new).
   - Select `gowthxm07/Resume_Matcher_Local_Agent`.
   - Set **Root Directory** to `frontend`.
   - Framework Preset: `Next.js`.
3. **Configure Environment Variables**:
   - Set `NEXT_PUBLIC_API_URL` = `http://127.0.0.1:8000/api`.
4. **Deploy**:
   - Click **Deploy**.
   - Verify build completes successfully with 12 static routes generated.
5. **Open Dashboard**:
   - Visit `https://<your-project>.vercel.app`.
   - Ensure the Local Agent is running on your machine:
     ```bash
     cd backend
     uvicorn app.main:app --host 127.0.0.1 --port 8000
     ```
   - The persistent header badge will switch to: `🟢 LOCAL AGENT CONNECTED (v1.0.0)`.
