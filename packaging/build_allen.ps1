param(
  [Parameter(Mandatory=$true)][string]$PublicKeyPath,
  [Parameter(Mandatory=$true)][string]$SigningPrivateKeyPath,
  [string]$ModelPath,
  [string]$LlamaServerPath,
  [switch]$DevelopmentBuild
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $repo
$python = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'Falta .venv de desarrollo. Ejecuta python -m venv .venv y requirements-build.txt.' }
$iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) { $iscc = 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' }
if (-not (Test-Path $iscc)) { throw 'No se encuentra ISCC.exe de Inno Setup 6.' }
$publicKey = (Resolve-Path $PublicKeyPath).Path
$privateKey = (Resolve-Path $SigningPrivateKeyPath).Path
$model = $ModelPath
$llama = $LlamaServerPath
$runtimeConfig = Join-Path $env:LOCALAPPDATA 'ALLEN\local_model.json'
if ((-not $model -or -not $llama) -and (Test-Path $runtimeConfig)) {
  $current = Get-Content $runtimeConfig -Raw | ConvertFrom-Json
  if (-not $model) { $model = [string]$current.model }
  if (-not $llama) { $llama = [string]$current.executable }
}
if (-not (Test-Path $model -PathType Leaf)) { throw 'No se encontró el GGUF Qwen configurado. Pasa -ModelPath.' }
if ([IO.Path]::GetFileName($model) -ne 'Qwen3.5-0.8B-Q8_0.gguf') { throw 'Esta build está fijada al modelo validado Qwen3.5-0.8B-Q8_0.gguf.' }
if (-not (Test-Path $llama -PathType Leaf)) { throw 'No se encontró llama-server.exe. Pasa -LlamaServerPath.' }
$packageRoot = Join-Path $repo 'dist\ALLEN'
$modelPack = Join-Path $repo 'dist\model-pack'
$version = '1.0.0'
$icon = Join-Path $repo 'frontend\assets\allen.ico'
if (-not (Test-Path $icon)) { throw 'No está frontend\assets\allen.ico derivado del logo oficial de Allen.' }
if ($DevelopmentBuild) { Write-Warning 'ESTA ES UNA BUILD DE DESARROLLO; no distribuir la clave pública de desarrollo ni el producto firmado con ella.' }

$keyHash = (Get-FileHash $publicKey -Algorithm SHA256).Hash.ToLowerInvariant()
$trustFile = Join-Path $repo 'licensing\trust_anchor.py'
$oldTrust = [IO.File]::ReadAllText($trustFile)
try {
  [IO.File]::WriteAllText($trustFile, "# Generated for this local build; public trust anchor only.`r`nPUBLIC_KEY_SHA256 = '$keyHash'`r`n", [Text.UTF8Encoding]::new($false))
  $common = @('--standalone','--zig','--assume-yes-for-downloads','--jobs=4')

  & $python -m nuitka @common '--windows-console-mode=disable' '--include-package=backend' '--include-package=licensing' '--include-package=uvicorn' '--include-package=cryptography' '--include-data-dir=frontend=frontend' '--include-data-dir=data=data' '--output-dir=build\backend' '--output-filename=allen_backend.exe' server.py
  if ($LASTEXITCODE -ne 0) { throw 'Falló la compilación standalone del backend.' }
  & $python -m nuitka @common '--windows-console-mode=disable' '--include-package=httpx' '--output-dir=build\ai' '--output-filename=allen_ai.exe' start_local_ai.py
  if ($LASTEXITCODE -ne 0) { throw 'Falló la compilación standalone del comprobador de IA.' }
  & $python -m nuitka @common '--windows-console-mode=disable' '--enable-plugin=tk-inter' '--include-package=licensing' '--include-package=cryptography' "--windows-icon-from-ico=$icon" '--file-version=1.0.0.0' '--product-version=1.0.0.0' '--product-name=ALLEN' '--output-dir=build\launcher' '--output-filename=ALLEN.exe' 'packaging\allen_gui.py'
  if ($LASTEXITCODE -ne 0) { throw 'Falló la compilación del launcher gráfico ALLEN.exe.' }
  & $python -m nuitka @common '--windows-console-mode=disable' '--include-package=licensing' '--include-package=cryptography' '--output-dir=build\register' '--output-filename=allen_register.exe' 'packaging\register_install.py'
  if ($LASTEXITCODE -ne 0) { throw 'Falló la compilación del registrador de instalación.' }

  New-Item -ItemType Directory -Force -Path $packageRoot,$modelPack | Out-Null
  $buildDists = @(
    (Join-Path $repo 'build\backend\server.dist'),
    (Join-Path $repo 'build\ai\start_local_ai.dist'),
    (Join-Path $repo 'build\launcher\allen_gui.dist'),
    (Join-Path $repo 'build\register\register_install.dist')
  )
  foreach ($stage in $buildDists) {
    if (-not (Test-Path $stage)) { throw "No existe la carpeta Nuitka standalone: $stage" }
    Get-ChildItem $stage -Force | ForEach-Object {
      $target = Join-Path $packageRoot $_.Name
      if (Test-Path $target) {
        if ($_.PSIsContainer -or (Get-FileHash $_.FullName).Hash -ne (Get-FileHash $target).Hash) {
          throw "Conflicto entre componentes standalone: $($_.Name). No se mezclaron dependencias incompatibles."
        }
      } else { Copy-Item $_.FullName $target -Recurse -Force }
    }
  }
  Copy-Item $icon (Join-Path $packageRoot 'allen.ico') -Force
  Copy-Item (Join-Path $repo 'frontend\assets\allen.png') (Join-Path $packageRoot 'allen.png') -Force
  Copy-Item $publicKey (Join-Path $packageRoot 'license_public_key.pem') -Force

  $runtime = Join-Path $packageRoot 'runtime\llama'
  New-Item -ItemType Directory -Force -Path $runtime | Out-Null
  $llamaRoot = Split-Path $llama
  Copy-Item $llama (Join-Path $runtime 'llama-server.exe') -Force
  Get-ChildItem $llamaRoot -Filter '*.dll' -File | Copy-Item -Destination $runtime -Force
  $ompNotice = Join-Path $llamaRoot 'LICENSE-LLVM-OpenMP'
  if (Test-Path $ompNotice) { Copy-Item $ompNotice $runtime -Force }
  $modelTarget = Join-Path $modelPack 'Qwen3.5-0.8B-Q8_0.gguf'
  if (-not (Test-Path $modelTarget)) { New-Item -ItemType HardLink -Path $modelTarget -Target (Resolve-Path $model).Path | Out-Null }
  if ((Get-Item $modelTarget).Length -ne (Get-Item $model).Length) { throw 'El GGUF preparado no coincide en tamaño con el modelo probado.' }
  Copy-Item (Join-Path $repo 'licenses\Apache-2.0.txt') (Join-Path $modelPack 'LICENSE-Apache-2.0.txt') -Force

  $packageLicenses = Join-Path $packageRoot 'licenses'
  New-Item -ItemType Directory -Force -Path $packageLicenses | Out-Null
  Get-ChildItem (Join-Path $repo 'licenses') -File | Copy-Item -Destination $packageLicenses -Force
  $pythonBase = & $python -c 'import sys; print(sys.base_prefix)'
  $pythonNotice = Join-Path $pythonBase 'LICENSE.txt'
  if (Test-Path $pythonNotice) { Copy-Item $pythonNotice (Join-Path $packageLicenses 'Python-LICENSE.txt') -Force }
  $critical = @('ALLEN.exe','allen_backend.exe','allen_ai.exe','allen_register.exe','license_public_key.pem','runtime/llama/llama-server.exe')
  $critical += Get-ChildItem $runtime -Filter '*.dll' -File | ForEach-Object { 'runtime/llama/' + $_.Name }
  $critical += Get-ChildItem (Join-Path $packageRoot 'frontend') -Recurse -File | ForEach-Object { $_.FullName.Substring($packageRoot.Length + 1).Replace('\','/') }
  $critical += Get-ChildItem (Join-Path $packageRoot 'data') -Recurse -File | ForEach-Object { $_.FullName.Substring($packageRoot.Length + 1).Replace('\','/') }
  $critical = $critical | Sort-Object -Unique
  $signArgs = @('tools\license_generator\allen_licensing.py','sign-manifest','--private',$privateKey,'--root',$packageRoot,'--version',$version,'--files') + $critical
  & $python @signArgs
  if ($LASTEXITCODE -ne 0) { throw 'No se pudo firmar manifest.allen.' }

  & $iscc (Join-Path $repo 'installer\ALLEN.iss')
  if ($LASTEXITCODE -ne 0) { throw 'Inno Setup no pudo compilar ALLEN_Setup.exe.' }
  Write-Host "Build preparada. Paquete: $packageRoot" -ForegroundColor Green
  Write-Host "Setup: $(Join-Path $repo 'dist\installer\ALLEN_Setup.exe')" -ForegroundColor Green
} finally {
  [IO.File]::WriteAllText($trustFile, $oldTrust, [Text.UTF8Encoding]::new($false))
}
