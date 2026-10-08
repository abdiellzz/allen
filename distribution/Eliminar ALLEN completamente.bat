@echo off
setlocal
set "ALLEN_REMOVE_TEMP=%TEMP%\ALLEN-remove-all-%RANDOM%%RANDOM%.ps1"
copy /y "%~dp0remove_allen.ps1" "%ALLEN_REMOVE_TEMP%" >nul
if errorlevel 1 (
  echo No se pudo preparar el eliminador de ALLEN.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%ALLEN_REMOVE_TEMP%" -SourceRoot "%~dp0"
set "RC=%ERRORLEVEL%"
del /q "%ALLEN_REMOVE_TEMP%" >nul 2>&1
if not "%RC%"=="0" pause
exit /b %RC%
