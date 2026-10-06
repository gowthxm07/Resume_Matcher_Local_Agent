# CareerCrew Local Agent Launcher for PowerShell
# Privacy-First Local Multi-Agent Job Application Optimizer
# Zero Cloud AI Dependencies

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "Starting CareerCrew Local Agent..." -ForegroundColor Cyan
Write-Host "===========================================================================" -ForegroundColor Cyan

# 1. Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python not found in PATH. Please install Python 3.10+ from python.org" -ForegroundColor Red
    exit 1
}

# 2. Check Ollama
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "[WARNING] Ollama CLI not found in PATH. Ensure Ollama is running at http://localhost:11434." -ForegroundColor Yellow
} else {
    Write-Host "[OK] Ollama detected." -ForegroundColor Green
}

# 3. Start Local Agent
Write-Host "[INFO] Launching CareerCrew Local Agent on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "[INFO] Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "[INFO] Press Ctrl+C to terminate the local agent." -ForegroundColor Gray
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "backend")
$env:PYTHONPATH = "."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
