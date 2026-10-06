# CareerCrew — Candidate User Guide

Welcome to **CareerCrew**, the privacy-first local multi-agent job application optimizer.

CareerCrew empowers software engineers, developers, and technology professionals to analyze, tailor, and optimize their resumes against job descriptions using verifiable evidence from their actual local Git repositories—without ever sending source code, personal data, or resumes to third-party cloud AI providers.

---

## 1. What is CareerCrew?

Traditional resume tools either:
1. Demand that you upload your private resumes and source code to remote cloud servers.
2. Blindly stuff unverified buzzwords into your resume, causing you to fail technical interview rounds or ATS background checks.

**CareerCrew takes a fundamentally different approach:**
- **Zero Cloud AI**: All language model inference runs locally on your machine via Ollama (`llama3.2:3b`).
- **Evidence-Grounded**: Every skill highlighted in your optimized resume is backed by verified code artifacts (dependencies, commit history, AST functions) discovered in your local projects.
- **Strict Anti-Hallucination Guardrail**: CareerCrew will **NEVER** fabricate a skill, company, metric, or project you do not possess, regardless of how much it would inflate your score.
- **Explainable Match Scoring**: Understand exactly why your resume matches or misses specific requirements across 5 transparent dimensions.

---

## 2. Privacy & Data Protection Guarantees

CareerCrew guarantees 100% workstation containment:

| Data Type | Storage Location | Cloud Transmission |
| :--- | :--- | :--- |
| **Resumes** | Local SQLite (`careercrew.db`) | **NEVER** |
| **Job Descriptions** | Local SQLite (`careercrew.db`) | **NEVER** |
| **Source Code Repositories** | Your Local Hard Drive | **NEVER** |
| **Code Snippets & ASTs** | Local Vector Store (`chroma`) | **NEVER** |
| **LLM Inference Prompts** | Local Ollama (`127.0.0.1:11434`) | **NEVER** |
| **Telemetry & Analytics** | None (Disabled) | **NEVER** |

No API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) are required, accepted, or configured.

---

## 3. Getting Started

### Step 1: Start the Local Agent
Choose the launcher for your environment:
- **Windows Batch**: Double-click or run `start_careercrew.bat`.
- **Windows PowerShell**: Run `.\start_careercrew.ps1`.
- **Manual Launch**:
  ```bash
  cd backend
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```

### Step 2: Open the Dashboard
- If running locally: Navigate to `http://localhost:3000`.
- If accessing a hosted dashboard: Open the dashboard URL and verify connection to `127.0.0.1:8000`.

### Step 3: Run the Setup Diagnostic
Navigate to the **Setup Wizard** (`/get-started`). CareerCrew will verify that your Python runtime, Ollama daemon, and local model weights (`llama3.2:3b` and `nomic-embed-text`) are active.

---

## 4. Connecting Local Software Repositories

CareerCrew inspects your actual software projects to verify technical competencies:

1. Click **Projects** in the navigation menu.
2. Select **Register Repository**.
3. Provide a friendly name and the absolute or relative path to a local project directory (e.g., `D:\Projects\my-fastapi-service`).
4. Click **Scan Repository**.

### What CareerCrew Analyzes:
- Package manifests (`package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`, `Dockerfile`).
- Syntax trees (import statements, framework decorators, database clients).
- Commit history (recent technical contributions).

### Security Boundaries:
- Repositories are scanned locally with read-only access.
- Path traversal sequences (such as `../../Windows/System32`) are blocked.
- Sensitive files (`.env`, private keys, passwords) are ignored by default.

---

## 5. Analyzing a Job Application

1. Click **Match Analysis**.
2. Upload your resume (`.pdf`, `.docx`, or `.txt`) or select a previously saved resume.
3. Paste the target job description or upload the job posting.
4. Click **Analyze Match**.

### Understanding Your Match Score:
CareerCrew provides a composite score from $0$ to $100\%$ derived from:
- **Required Skill Match (40%)**: Coverage of must-have technologies.
- **Preferred Skill Match (15%)**: Coverage of nice-to-have technologies.
- **Experience Match (20%)**: Alignment of seniority and years of experience.
- **Project Evidence Match (15%)**: Direct corroboration from your connected code repositories.
- **Semantic Similarity (10%)**: Conceptual alignment computed locally using `nomic-embed-text`.

Each requirement is explicitly classified as:
- ✅ **MATCH**: Skill explicitly found and corroborated.
- 🟡 **PARTIAL MATCH**: Related skill identified (e.g., PostgreSQL vs MySQL).
- ❌ **MISSING**: Requirement absent from both resume and verified code.

---

## 6. Optimizing Your Resume

Once baseline analysis is complete, click **Optimize Resume**.

### How Optimization Works:
1. **Targeted Rewording**: CareerCrew suggests improvements for bullet points that fail to clearly showcase your proven skills.
2. **Technical Grounding**: Vague statements like *"Worked on the backend"* are enhanced using your registered project evidence: *"Engineered asynchronous REST APIs using FastAPI and PostgreSQL"*.
3. **Strict Fact Checking**: Before any modification is presented to you, CareerCrew's fact-checking service cross-examines the text. If a proposed change introduces an unverified skill or made-up statistic, it is rejected.
4. **ATS Compatibility Scoring**: Each iteration is evaluated for machine parseability, clean heading structure, and standard bullet formatting.

---

## 7. Reviewing Versions and Audit History

CareerCrew maintains an immutable version ledger:
- **ORIGINAL (Version 0)**: Your initial resume, preserved untouched.
- **CANDIDATE (Iterations 1...N)**: Iterative improvements with line-by-line diffs.
- **FINAL**: Your chosen production version.

Click **Audit Trail** on any version to see:
- Exactly why each line was changed.
- Which repository file provided the grounding evidence.
- The ATS improvement score.

---

## 8. Operating Modes

### Mode A: Fully Localhost (Recommended for Maximum Isolation)
Both the web dashboard (`localhost:3000`) and the AI agent (`127.0.0.1:8000`) run on your local computer. This mode functions completely offline without internet access.

### Mode B: Hosted Dashboard + Local Agent
The dashboard UI is loaded from a static web host (such as Vercel), but the browser connects directly to `http://127.0.0.1:8000` on your machine. All AI processing, file storage, and code scanning remain 100% local. Zero candidate data touches cloud servers.

---

## 9. Troubleshooting

### Issue: "Ollama Unreachable" in Setup Wizard
- Verify Ollama is running in your system tray or terminal (`ollama list`).
- Run `ollama serve` in a terminal window.

### Issue: "Model llama3.2:3b Missing"
- Open your terminal and run:
  ```bash
  ollama run llama3.2:3b
  ```
- Also download the embedding model:
  ```bash
  ollama pull nomic-embed-text
  ```

### Issue: "Port 8000 already in use"
- Check what process is occupying port 8000 (`netstat -ano | findstr :8000`).
- Terminate the conflicting process or update the port in `.env`.
