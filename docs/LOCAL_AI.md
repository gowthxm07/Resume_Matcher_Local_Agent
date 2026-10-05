# Local AI & Privacy Model

## 1. Why Local-Only AI?

Resumes, job descriptions, and personal codebases contain highly sensitive personal and proprietary information:
- Full legal names, home addresses, phone numbers, and personal email addresses
- Complete employment histories, current employer projects, and proprietary metrics
- Personal code repositories containing unpublished IP, commit patterns, and architecture notes

Traditional AI tools upload these raw documents to third-party cloud LLMs (OpenAI, Anthropic, Google, AWS), exposing candidates to:
- Third-party data retention and potential model training on private resumes
- Data breach risks at centralized cloud aggregators
- Uncontrollable API price changes, rate limits, and outages

**CareerCrew's core principle is complete data sovereignty**: your data stays exclusively on your local workstation.

---

## 2. Technology Choices: Ollama & Llama 3.2:3b

### Why Ollama?
- **Zero Configuration Inference**: Packages llama.cpp into a clean background daemon on Windows, macOS, and Linux.
- **RESTful API**: Exposes clean HTTP endpoints (`/api/generate`, `/api/embeddings`, `/api/tags`) running on `localhost:11434`.
- **Hardware Acceleration**: Automatically detects and leverages NVIDIA CUDA, AMD ROCm, Apple Metal, or AVX2 CPU instructions without manual compilation.
- **Completely Air-Gapped**: Once models are pulled, Ollama needs zero network access.

### Why Llama 3.2:3b?
- **Efficiency & Footprint**: At 3 billion parameters (approx. 2.0 GB quantized), Llama 3.2:3b runs comfortably on standard consumer laptops with 8GB-16GB RAM or entry-level GPUs.
- **Instruction Following**: Specifically tuned for structured extraction, JSON output, and analytical reasoning.
- **Low Inference Latency**: Produces fast local responses (typically 50-200ms per token on modern hardware), enabling responsive iterative optimization loops.

### Why nomic-embed-text?
- Compact 137M parameter embedding model running locally via Ollama.
- Produces 768-dimensional dense vectors with an 8192 token context window, ideal for embedding full resume sections and job descriptions.

---

## 3. How Local Inference Works in CareerCrew

1. The frontend or test suite issues an instruction request to the FastAPI backend.
2. The backend constructs a prompt with strict system guardrails.
3. The request is dispatched via HTTP over local loopback (`127.0.0.1:11434`) to the local Ollama daemon.
4. Ollama executes local weights on the CPU/GPU and streams or returns the token completion.
5. No network packets leave the machine.

---

## 4. How to Verify Zero External API Calls Are Made

You can mathematically and empirically verify that CareerCrew makes zero cloud API calls:

### 1. Codebase Verification
Search the entire repository for cloud LLM SDKs or environment keys:
```bash
# Verify no OpenAI/Anthropic/Gemini keys or endpoints exist in the codebase:
grep -rn "api.openai.com" .
grep -rn "api.anthropic.com" .
grep -rn "generativelanguage.googleapis.com" .
grep -rn "OPENAI_API_KEY" .
grep -rn "ANTHROPIC_API_KEY" .
grep -rn "GEMINI_API_KEY" .
```
*(All return zero matches in application code)*

### 2. Configuration Guardrails
`app.core.config.Settings` explicitly validates `LLM_PROVIDER`:
```python
@field_validator("LLM_PROVIDER")
@classmethod
def validate_local_provider_only(cls, v: str) -> str:
    prohibited = ["openai", "anthropic", "gemini", "bedrock", "azure", "cohere"]
    if any(cloud in v.lower() for cloud in prohibited):
        raise ValueError("Cloud providers prohibited by CareerCrew privacy architecture.")
    return v
```

### 3. Network Isolation Test (Air-Gap Test)
1. Turn off your Wi-Fi or disconnect your ethernet cable.
2. Run backend tests:
   ```bash
   cd backend
   python -m pytest tests -v
   ```
3. Run the application:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
4. Perform an extraction test or LLM test from the dashboard at `http://localhost:3000`.
5. Observe that the entire system functions normally without internet connectivity.

---

## 5. Security & Privacy Architecture

- **No Full Document Logging**: Raw document contents and full parsed resumes are filtered from console and file logs (`PrivacyFilter` redacts strings exceeding length thresholds).
- **No Arbitrary URL Exposures**: File contents are never exposed via static web servers or predictable public file URLs.
- **Path Sanitization**: All uploaded filenames are stripped of path traversal characters (`..`, `/`, `\`) and null bytes (`\x00`).
- **File Size Caps**: Uploaded files are capped at 10MB to prevent memory exhaustion.
- **Isolated Local Storage**: All databases and vector indexes live in the git-ignored `./data/` folder on your disk.
