param(
  [string]$InstallDir = "$env:LOCALAPPDATA\ALLEN\app",
  [switch]$SkipDependencies
)
$ErrorActionPreference = 'Stop'
$source = (Resolve-Path (Join-Path $PSScriptRoot '.')).Path
$target = [IO.Path]::GetFullPath($InstallDir)
if ($target -eq $source) { throw 'Elige una carpeta de instalación distinta al repositorio.' }

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { throw 'ALLEN necesita Python 3.11 o superior. Instálalo desde https://www.python.org/downloads/windows/ y vuelve a ejecutar este instalador.' }
$version = & $python.Source -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$version -lt [version]'3.11') { throw "Python $version no es compatible; se necesita Python 3.11 o superior." }

New-Item -ItemType Directory -Force -Path $target | Out-Null
Get-ChildItem $source -Force | Where-Object { $_.Name -notin @('.git','.venv','__pycache__','.pytest_cache','models','data') } | ForEach-Object {
  Copy-Item $_.FullName (Join-Path $target $_.Name) -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $target 'data') | Out-Null
if (Test-Path (Join-Path $source 'data\library')) { Copy-Item (Join-Path $source 'data\library') (Join-Path $target 'data') -Recurse -Force }
$venv = Join-Path $target '.venv'
if (-not (Test-Path (Join-Path $venv 'Scripts\python.exe'))) { & $python.Source -m venv $venv }
if (-not $SkipDependencies) { & (Join-Path $venv 'Scripts\python.exe') -m pip install --disable-pip-version-check -r (Join-Path $target 'requirements.txt') }
$launcher = Join-Path $target 'Iniciar ALLEN.bat'
@("@echo off", "cd /d `"$target`"", "`.venv\Scripts\python.exe`" start_local_ai.py", "`.venv\Scripts\python.exe`" server.py --open") | Set-Content -LiteralPath $launcher -Encoding ascii
Write-Host "ALLEN instalado en $target"
Write-Host "Inicia con: $launcher"
Write-Host 'El modelo GGUF y llama.cpp se configuran aparte en %LOCALAPPDATA%\ALLEN\local_model.json.'
