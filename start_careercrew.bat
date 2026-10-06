@echo off
REM CareerCrew Local Agent Launcher for Windows
REM Privacy-First Local Multi-Agent Job Application Optimizer
REM Zero Cloud AI Dependencies

echo ===========================================================================
echo Starting CareerCrew Local Agent...
echo ===========================================================================

REM 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH. Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM 2. Check Ollama
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Ollama CLI not found in PATH.
    echo Ensure Ollama is running at http://localhost:11434 before starting analysis.
)

REM 3. Start Local Agent
echo [INFO] Launching CareerCrew Local Agent on http://127.0.0.1:8000
echo [INFO] Swagger Docs: http://127.0.0.1:8000/docs
echo [INFO] Press Ctrl+C to terminate the local agent.
echo.

cd /d "%~dp0backend"
set PYTHONPATH=.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
