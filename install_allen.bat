@echo off
setlocal
cd /d "%~dp0"
title Instalador de ALLEN
echo ========================================
echo          INSTALADOR DE ALLEN
echo ========================================
echo.
set "LLAMA_FLAG="
where winget >nul 2>&1
if errorlevel 1 goto install
powershell -NoProfile -Command "$p=Join-Path $env:LOCALAPPDATA 'ALLEN\local_model.json'; if(Test-Path $p){$c=Get-Content $p -Raw|ConvertFrom-Json; if(Test-Path $c.executable){exit 1}}; exit 0" >nul 2>&1
if errorlevel 1 goto install
choice /C SN /N /M "No se encontro llama-server. Instalar llama.cpp desde WinGet? [S/N] "
if errorlevel 2 goto install
set "LLAMA_FLAG=-InstallLlamaCpp"
:install
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_allen.ps1" %LLAMA_FLAG%
if errorlevel 1 (
  echo.
  echo La instalacion no pudo completarse. Revisa el mensaje anterior.
  pause
  exit /b 1
)
echo.
echo Instalacion lista. Usa Iniciar_ALLEN.bat.
pause
