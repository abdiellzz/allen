@echo off
setlocal
cd /d "%~dp0"
echo Iniciando ALLEN...
set "ALLEN_PY=python"
python -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
if not errorlevel 1 goto python_ready
set "ALLEN_PY=py -3"
py -3 -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>&1
if errorlevel 1 (
  echo Instala Python 3.11 o superior desde https://www.python.org/downloads/windows/
  echo Durante la instalacion, marca Add Python to PATH.
  pause
  exit /b 1
)
:python_ready
if exist ".venv\Scripts\python.exe" goto environment_ready
%ALLEN_PY% -m venv .venv
if errorlevel 1 goto install_error
:environment_ready
".venv\Scripts\python.exe" -c "from importlib.metadata import version; assert version('fastapi')=='0.136.3'; assert version('uvicorn')=='0.49.0'; assert version('httpx')=='0.28.1'" >nul 2>&1
if not errorlevel 1 goto start_app
echo Instalando dependencias. Esta primera vez necesitas Internet.
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto install_error
:start_app
".venv\Scripts\python.exe" start_local_ai.py
".venv\Scripts\python.exe" server.py --open
if errorlevel 1 (
  echo No se pudo iniciar ALLEN. Comprueba que no este abierto en otra ventana.
  pause
)
exit /b
:install_error
echo No se pudieron instalar las dependencias. Comprueba Python y tu conexion.
echo Una vez instaladas, ALLEN no necesita Internet para iniciar.
pause
exit /b 1
