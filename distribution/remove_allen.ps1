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
    (Normalize-Path $env:SystemRoot),
    (Normalize-Path (Join-Path $env:USERPROFILE "Downloads")),
    (Normalize-Path ([Environment]::GetFolderPath("Desktop"))),
    (Normalize-Path ([Environment]::GetFolderPath("MyDocuments")))
  )
  $driveRoot = Normalize-Path ([IO.Path]::GetPathRoot($resolved))
  if (($blocked -contains $resolved) -or ($resolved -eq $driveRoot)) {
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

# Remove recognized ALLEN distribution downloads without touching unrelated files.
$downloads = Join-Path $env:USERPROFILE "Downloads"
if (Test-Path -LiteralPath $downloads) {
  $downloadPatterns = @(
    "ALLEN-*-Setup-Windows-x64.exe",
    "ALLEN-*-Portable-Windows-x64.zip",
    "allen-installer*.zip",
    "allen-portable*.zip"
  )
  foreach ($pattern in $downloadPatterns) {
    Get-ChildItem -LiteralPath $downloads -Filter $pattern -File -ErrorAction SilentlyContinue |
      ForEach-Object {
        Write-Host "Eliminando descarga: $($_.FullName)"
        Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue
      }
  }
}

# If this remover came from a portable/extracted distribution, remove that folder
# too. Never trust SourceRoot merely because it contains a file named ALLEN.exe:
# the caller controls SourceRoot and it could otherwise point at Downloads or
# another broad user directory.
$source = Normalize-Path $SourceRoot
if ($source) {
  $portableFlag = Join-Path $source "portable.flag"
  $allenExe = Join-Path $source "ALLEN.exe"
  $internalDir = Join-Path $source "_internal"
  $removeScript = Join-Path $source "remove_allen.ps1"
  $knownInstalled = Normalize-Path $installedApp
  $isPortableRoot = (
    (Test-Path -LiteralPath $portableFlag) -and
    (Test-Path -LiteralPath $allenExe) -and
    (Test-Path -LiteralPath $internalDir) -and
    (Test-Path -LiteralPath $removeScript)
  )
  if (($source -eq $knownInstalled) -or $isPortableRoot) {
    Safe-Remove $source
  } else {
    Write-Warning "SourceRoot no reconocido como una instalación ALLEN; no se elimina: $source"
  }
}

Write-Host ""
Write-Host "ALLEN fue eliminado de este usuario de Windows." -ForegroundColor Green
Write-Host "Los modelos GGUF y llama.cpp externos se conservaron." -ForegroundColor DarkGray
Start-Sleep -Seconds 2
