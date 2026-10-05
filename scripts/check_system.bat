@echo off
echo ===================================================
echo CareerCrew Local-Only System Verification
echo ===================================================
echo.
echo Checking Python...
python --version
echo.
echo Checking Node.js...
node --version
echo.
echo Checking Ollama...
ollama list
echo.
echo Checking Backend Health Endpoint...
powershell -Command "try { (Invoke-RestMethod -Uri http://127.0.0.1:8000/api/health -TimeoutSec 3).status } catch { 'Backend not currently running on :8000' }"
echo.
echo Verification complete.
