@echo off
echo Running CareerCrew Backend Automated Test Suite...
cd /d "%~dp0\..\backend"
python -m pytest tests -v
