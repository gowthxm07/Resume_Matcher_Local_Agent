# CareerCrew — Live Demonstration Script (5–10 Minutes)

This script is designed for live product demonstrations, video recordings, technical walkthroughs, and portfolio presentations.

---

## Overview & Demo Narrative

| Timing | Scene | Focus | Key Takeaway |
| :--- | :--- | :--- | :--- |
| **0:00 - 1:00** | Scene 1: The Problem | Privacy vs AI Hallucination | Candidates need tailored resumes, but cloud AI invents facts and leaks IP. |
| **1:00 - 2:00** | Scene 2: Architectural Tour | Local Agent Architecture | Localhost agent + browser UI; zero cloud tokens or subscriptions. |
| **2:00 - 3:00** | Scene 3: Setup Diagnostic | Deterministic Compatibility | Live check of Python, CrewAI, Ollama `llama3.2:3b`, and `nomic-embed-text`. |
| **3:00 - 4:30** | Scene 4: Code Evidence Scan | Grounding in Real Repositories | Inspecting ASTs and manifests to produce verified evidence records. |
| **4:30 - 6:00** | Scene 5: Baseline Match | Explainable Scoring | 5-dimension breakdown with transparent requirement classification. |
| **6:00 - 7:30** | Scene 6: Fact-Checking Defense | Anti-Hallucination Guardrail | Provocative test: showing strict rejection of ungrounded cloud claims. |
| **7:30 - 8:30** | Scene 7: ATS & Versioning | Audit Trail & Immutable Diffs | Preserving Original, tracking candidate iterations, ATS disclaimer. |
| **8:30 - 9:00** | Scene 8: Privacy Proof | Terminal Invariant Audit | Verifying zero external network calls during analysis. |

---

## Detailed Demonstration Sequence

### Scene 1: Introduction & The Core Problem (0:00 - 1:00)
- **Speaker**:
  > *"When applying for software engineering roles, candidates face two major challenges: cloud AI tools leak their private source code and resumes, while generative tools hallucinate technologies and metrics that candidates can't defend in technical interviews.*
  > *CareerCrew solves this with a privacy-first, local multi-agent system. Everything runs on your machine using Ollama and CrewAI, and every suggested improvement is grounded in your actual software repositories."*

---

### Scene 2: Architecture & Privacy Invariant (1:00 - 2:00)
- **Action**: Open terminal and display the running backend:
  ```powershell
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```
- **Show**: Point out the terminal logs:
  - `Local LLM Provider: ollama (llama3.2:3b)`
  - `Local Embeddings: nomic-embed-text`
  - `ZERO external cloud APIs permitted or configured.`
- **Highlight**: Explain the decoupled architecture:
  > *"Whether the dashboard is served locally on localhost:3000 or loaded from Vercel, the AI agent binds strictly to 127.0.0.1. Zero bytes of candidate resume or code leave this computer."*

---

### Scene 3: Setup Diagnostic & Capability Check (2:00 - 3:00)
- **Action**: In the browser, navigate to `/get-started`.
- **Show**: Click **Run Diagnostics**.
- **Observation**:
  - Show green checks for Python, FastAPI, Ollama, ChromaDB, and SQLite.
  - Point to `/api/local-agent/capabilities`:
    > *"Notice that interview intelligence is explicitly reported as false. CareerCrew is honest about its capabilities and never pretends to support features that are not yet production-verified."*

---

### Scene 4: Repository Evidence Discovery (3:00 - 4:30)
- **Action**: Navigate to `/projects`.
- **Action**: Register `backend/tests/fixtures/repos/python_fastapi_backend` and click **Scan**.
- **Observation**:
  - Show the scanned dependencies: `FastAPI`, `Python`, `SQLAlchemy`, `PostgreSQL`, `Docker`.
  - Highlight the confidence badges: `VERIFIED (0.95)` based on package manifests and AST import trees.
  - Explain:
    > *"These records become the ground truth. CareerCrew will only allow resume rewrites that reference these verified technical artifacts."*

---

### Scene 5: Candidate Intake & Baseline Match (4:30 - 6:00)
- **Action**: Navigate to `/analysis`.
- **Action**: Load **Dataset A (Alex Developer)** against **Senior Python Backend Engineer**.
- **Click**: **Analyze Match**.
- **Show**: The Explainable Match Score ($85.6\%$):
  - Required Skills: $100\%$ (Python, FastAPI, PostgreSQL, Git matched).
  - Experience: $90\%$.
  - Project Evidence: High corroboration.
  - Explain the requirement table:
    > *"Every requirement is categorized as MATCH, PARTIAL_MATCH, or MISSING. Candidates know exactly where they stand without guessing."*

---

### Scene 6: Adversarial Anti-Hallucination Demonstration (6:00 - 7:30)
- **Action**: Load **Dataset B (Jordan Frontend)** applying for **Lead Cloud Architect**.
- **Show**:
  - Match score drops to $42.2\%$ due to missing AWS, Kubernetes, and Terraform.
- **Trigger Optimization**:
  - Simulate an adversarial suggestion: *"Engineered AWS Kubernetes cluster scaling throughput by 10x with 99.999% uptime."*
- **Show**: The Fact Checker output:
  - **Status**: `UNSUPPORTED / REJECTED`.
  - **Flagged Claims**: `AWS` (no repository evidence), `Kubernetes` (no repository evidence), `10x` (unverified metric).
  - **Explanation**:
    > *"CareerCrew's fact checker stops resume embellishment in its tracks. It strips fabricated metrics and rejects ungrounded cloud claims because the candidate has zero code evidence backing them."*

---

### Scene 7: ATS Validation, Version Ledger & Diffs (7:30 - 8:30)
- **Action**: Navigate to the **Versions** tab.
- **Show**:
  - **Version 0 (ORIGINAL)**: Unmodified candidate resume.
  - **Version 1 (CANDIDATE)**: Evidence-grounded enhancement.
  - **ATS Score**: $100\%$ parseability with standard section headings.
  - **Mandatory Disclaimer**:
    > *"ATS scores are heuristic estimates of machine parseability and keyword alignment, not guarantees of employer ATS platform outcomes."*
  - **Diff View**: Highlight clean green/red additions showing only grounded improvements.

---

### Scene 8: Verification & Privacy Proof (8:30 - 9:00)
- **Action**: Switch to terminal. Run:
  ```powershell
  python scripts/verify_phase7.py
  ```
- **Show**:
  - All 22 automated product verification checks pass with exit code 0.
- **Conclusion**:
  > *"CareerCrew proves that developers do not need to sacrifice their privacy or risk their professional integrity to build high-converting, tailored job applications. Thank you!"*
