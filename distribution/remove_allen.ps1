param(
  [string]$SourceRoot = "",
  [switch]$Force
)

$ErrorActionPreference = "SilentlyContinue"

function Normalize-Path([string]$PathValue) {
  if (-not $PathValue) { return $null }
  try { return [IO.Path]::GetFullPath($PathValue.TrimEnd('\')) } catch { return $null }
}

function Safe-Remove([string]$PathValue) {
  $resolved = Normalize-Path $PathValue
  if (-not $resolved) { return }
  if (-not (Test-Path -LiteralPath $resolved)) { return }

  $blocked = @(
    (Normalize-Path $env:USERPROFILE),
    (Normalize-Path $env:LOCALAPPDATA),
    (Normalize-Path $env:APPDATA),
    (Normalize-Path $env:TEMP),
    (Normalize-Path $env:SystemRoot)
  )
  if ($blocked -contains $resolved) {
    Write-Warning "Ruta protegida omitida: $resolved"
    return
  }

  Write-Host "Eliminando: $resolved"
  Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction SilentlyContinue
}

if (-not $Force) {
  Write-Host ""
  Write-Host "===============================================" -ForegroundColor Yellow
  Write-Host "        ELIMINAR ALLEN COMPLETAMENTE" -ForegroundColor Yellow
  Write-Host "===============================================" -ForegroundColor Yellow
  Write-Host ""
  Write-Host "Esto elimina de este usuario de Windows:"
  Write-Host "- La aplicación ALLEN instalada o portable"
  Write-Host "- Perfiles, progreso, quizzes y base de datos"
  Write-Host "- Backups y snapshots locales de ALLEN"
  Write-Host "- Configuración de IA local guardada por ALLEN"
  Write-Host "- Accesos directos y archivos temporales de ALLEN"
  Write-Host ""
  Write-Host "NO elimina modelos GGUF ni llama.cpp externos."
  Write-Host "NO elimina documentos .allenpack o backups que hayas copiado manualmente fuera de las carpetas de ALLEN."
  Write-Host ""
  $answer = Read-Host "Escribe BORRAR para continuar"
  if ($answer -cne "BORRAR") {
    Write-Host "Cancelado. No se eliminó nada."
    exit 0
  }
}

# Stop only ALLEN-owned launcher processes. Do not kill llama-server because it can
# be shared with other local applications.
Get-Process -Name "ALLEN" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

$localData = Join-Path $env:LOCALAPPDATA "ALLEN"
$installedApp = Join-Path $env:LOCALAPPDATA "Programs\ALLEN"
$legacyApp = Join-Path $localData "app"
$startMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\ALLEN"
$desktopLink = Join-Path ([Environment]::GetFolderPath("Desktop")) "ALLEN.lnk"
$desktopPublic = Join-Path $env:PUBLIC "Desktop\ALLEN.lnk"

# Prefer the official Inno Setup uninstaller so Windows' uninstall registry entry
# is removed cleanly.
$uninstaller = Join-Path $installedApp "unins000.exe"
if (Test-Path -LiteralPath $uninstaller) {
  Write-Host "Ejecutando el desinstalador de ALLEN..."
  Start-Process -FilePath $uninstaller -ArgumentList "/VERYSILENT","/SUPPRESSMSGBOXES","/NORESTART" -Wait -ErrorAction SilentlyContinue
}

Safe-Remove $localData
Safe-Remove $installedApp
Safe-Remove $legacyApp
Safe-Remove $startMenu
Remove-Item -LiteralPath $desktopLink -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $desktopPublic -Force -ErrorAction SilentlyContinue

# Remove only ALLEN-named temporary paths, never the user's entire TEMP folder.
Get-ChildItem -LiteralPath $env:TEMP -Force -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -like "ALLEN*" -or $_.Name -like "allen-*" } |
  ForEach-Object { Safe-Remove $_.FullName }

# If this remover came from a portable/extracted distribution, remove that folder
# too. The script itself runs from TEMP, so the source folder is not locked.
$source = Normalize-Path $SourceRoot
if ($source) {
  $portableFlag = Join-Path $source "portable.flag"
  $allenExe = Join-Path $source "ALLEN.exe"
  $knownInstalled = Normalize-Path $installedApp
  if ((Test-Path -LiteralPath $portableFlag) -or (Test-Path -LiteralPath $allenExe) -or $source -eq $knownInstalled) {
    Safe-Remove $source
  }
}

Write-Host ""
Write-Host "ALLEN fue eliminado de este usuario de Windows." -ForegroundColor Green
Write-Host "Los modelos GGUF y llama.cpp externos se conservaron." -ForegroundColor DarkGray
Start-Sleep -Seconds 2
