@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo No se encontro el entorno virtual de ALLEN.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" scripts\allen_launcher.py --help >nul 2>&1
".venv\Scripts\python.exe" scripts\allen_stopper.py
if errorlevel 1 pause
