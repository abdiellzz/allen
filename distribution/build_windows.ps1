param(
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path (Join-Path $PSScriptRoot ".."))

$version = (Get-Content -LiteralPath "VERSION" -Raw).Trim()
if (-not ($version -match '^\d+\.\d+\.\d+$')) {
  throw "VERSION no contiene una versión SemVer válida."
}

& $Python -m pip install --disable-pip-version-check -r requirements.txt -r requirements-build.txt
& $Python -m PyInstaller --noconfirm --clean distribution/allen.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller falló." }

$built = Resolve-Path "dist\ALLEN"
& "$built\ALLEN.exe" --self-test
if ($LASTEXITCODE -ne 0) { throw "El ejecutable empaquetado no pasó el self-test." }

& "$built\ALLEN.exe" --server-smoke-test
if ($LASTEXITCODE -ne 0) { throw "El ejecutable empaquetado no pudo iniciar el servidor local." }

Remove-Item "artifacts" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "artifacts" | Out-Null
Remove-Item "build\distribution" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "build\distribution" | Out-Null

$portable = "build\distribution\ALLEN-Portable"
Copy-Item $built $portable -Recurse
New-Item -ItemType File -Path (Join-Path $portable "portable.flag") | Out-Null
Copy-Item "distribution\PORTABLE_README.txt" (Join-Path $portable "LEEME-PORTABLE.txt")
Copy-Item "distribution\remove_allen.ps1" (Join-Path $portable "remove_allen.ps1")
Copy-Item "distribution\Eliminar ALLEN completamente.bat" (Join-Path $portable "Eliminar ALLEN completamente.bat")

$portableZip = "artifacts\ALLEN-$version-Portable-Windows-x64.zip"
Compress-Archive -Path "$portable\*" -DestinationPath $portableZip -CompressionLevel Optimal

$installerSource = "build\distribution\ALLEN-Installer"
Copy-Item $built $installerSource -Recurse
Copy-Item "distribution\remove_allen.ps1" (Join-Path $installerSource "remove_allen.ps1")
Copy-Item "distribution\Eliminar ALLEN completamente.bat" (Join-Path $installerSource "Eliminar ALLEN completamente.bat")

$iscc = Get-ChildItem "C:\Program Files (x86)\Inno Setup *\ISCC.exe" -ErrorAction SilentlyContinue |
  Sort-Object FullName -Descending |
  Select-Object -First 1
if (-not $iscc) {
  $iscc = Get-ChildItem "C:\Program Files\Inno Setup *\ISCC.exe" -ErrorAction SilentlyContinue |
    Sort-Object FullName -Descending |
    Select-Object -First 1
}
if (-not $iscc) { throw "No se encontró ISCC.exe. Instala Inno Setup." }

$sourceFull = (Resolve-Path $installerSource).Path
$outputFull = (Resolve-Path "artifacts").Path
& $iscc.FullName "/DMyAppVersion=$version" "/DSourceDir=$sourceFull" "/DOutputDir=$outputFull" "distribution\installer.iss"
if ($LASTEXITCODE -ne 0) { throw "Inno Setup falló." }

$installer = Get-ChildItem "artifacts\ALLEN-$version-Setup-Windows-x64.exe" -ErrorAction Stop
Write-Host "Portable: $portableZip"
Write-Host "Installer: $($installer.FullName)"
