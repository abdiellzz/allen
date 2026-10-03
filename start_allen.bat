@echo off
setlocal
cd /d "%~dp0"
title ALLEN - Inicio
echo ========================================
echo               ALLEN
echo       Iniciando experiencia...
echo ========================================
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  echo No se encontro el entorno de ALLEN. Ejecuta Instalar_ALLEN.bat primero.
  goto error
)
"%PYTHON_EXE%" -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
if errorlevel 1 (
  echo El entorno Python no es valido. Ejecuta Instalar_ALLEN.bat.
  goto error
)
echo [1/4] Python: OK
"%PYTHON_EXE%" -c "from importlib.metadata import version; assert version('fastapi')=='0.136.3'; assert version('uvicorn')=='0.49.0'; assert version('httpx')=='0.28.1'; assert version('qrcode')=='8.2'" >nul 2>&1
if errorlevel 1 (
  echo Dependencias incompletas. Ejecuta Instalar_ALLEN.bat con conexion a Internet.
  goto error
)
echo [2/4] Dependencias: OK
set "AI_STATUS=%TEMP%\allen-ai-status-%RANDOM%.txt"
"%PYTHON_EXE%" start_local_ai.py --status-file "%AI_STATUS%"
if errorlevel 1 goto error
type "%AI_STATUS%" | findstr /X /C:"ready" >nul
if errorlevel 1 goto demo_check
echo [3/4] IA local lista; inferencia real confirmada
goto start_backend
:demo_check
type "%AI_STATUS%" | findstr /X /C:"demo" >nul
if errorlevel 1 goto error
echo [3/4] Modo demo activado explicitamente en Configuracion
:start_backend
"%PYTHON_EXE%" scripts\allen_launcher.py --ai-status "%AI_STATUS%"
set "LAUNCH_RESULT=%ERRORLEVEL%"
if exist "%AI_STATUS%" del "%AI_STATUS%" >nul 2>&1
if not "%LAUNCH_RESULT%"=="0" goto error
exit /b 0
:error
echo.
echo No se pudo iniciar ALLEN. Consulta logs\launcher.log si existe.
pause
exit /b 1
