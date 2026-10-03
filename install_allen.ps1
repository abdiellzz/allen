param(
  [string]$InstallDir = "$env:LOCALAPPDATA\ALLEN\app",
  [switch]$SkipDependencies,
  [switch]$InstallLlamaCpp
)
$ErrorActionPreference = 'Stop'
$Host.UI.RawUI.WindowTitle = 'Instalador de ALLEN'
Write-Host '========================================' -ForegroundColor DarkCyan
Write-Host '          INSTALADOR DE ALLEN' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor DarkCyan
if ($env:OS -ne 'Windows_NT') { throw 'Este instalador está diseñado para Windows.' }

$source = (Resolve-Path (Join-Path $PSScriptRoot '.')).Path
$target = [IO.Path]::GetFullPath($InstallDir)
if ($target -eq $source) { throw 'Elige una carpeta de instalación distinta al repositorio.' }
$pythonCommand = $null
$pythonArgs = @()
$version = $null
foreach ($candidate in @((Get-Command python -ErrorAction SilentlyContinue),(Get-Command py -ErrorAction SilentlyContinue)) | Where-Object { $_ }) {
  $candidateArgs = if ($candidate.Name -eq 'py.exe' -or $candidate.Name -eq 'py') { @('-3') } else { @() }
  try {
    $candidateVersion = & $candidate.Source @candidateArgs -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
    if ($LASTEXITCODE -eq 0 -and [version]$candidateVersion -ge [version]'3.11') {
      $pythonCommand = $candidate
      $pythonArgs = $candidateArgs
      $version = $candidateVersion
      break
    }
  } catch { }
}
if (-not $pythonCommand) {
  throw 'ALLEN necesita Python 3.11 o posterior. No se encontró una instalación compatible. Instálalo desde https://www.python.org/downloads/windows/ y vuelve a ejecutar este instalador.'
}
Write-Host "[1/6] Python ${version}: OK" -ForegroundColor Green
& $pythonCommand.Source @pythonArgs -m pip --version *> $null
if ($LASTEXITCODE -ne 0) { throw 'Python existe, pero pip no está disponible. Repara la instalación de Python y vuelve a ejecutar el instalador.' }

if (-not (Test-Path $target)) { New-Item -ItemType Directory -Force -Path $target | Out-Null }
$drive = [IO.Path]::GetPathRoot($target)
$freeBytes = (Get-PSDrive -Name $drive.Substring(0,1)).Free
if ($freeBytes -lt 1GB) { throw 'Hay menos de 1 GB libre para instalar ALLEN y sus dependencias.' }
Write-Host '[2/6] Espacio en disco y carpeta de destino: OK' -ForegroundColor Green

Get-ChildItem $source -Force | Where-Object { $_.Name -notin @('.git','.venv','__pycache__','.pytest_cache','models','data','logs','output','tmp') } | ForEach-Object {
  Copy-Item $_.FullName (Join-Path $target $_.Name) -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $target 'data') | Out-Null
Get-ChildItem (Join-Path $source 'data') -Force | Where-Object { $_.Name -ne 'library' } | ForEach-Object {
  Copy-Item $_.FullName (Join-Path $target 'data') -Recurse -Force
}
if (Test-Path (Join-Path $source 'data\library')) { Copy-Item (Join-Path $source 'data\library') (Join-Path $target 'data') -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $target 'logs') | Out-Null
$venv = Join-Path $target '.venv'
$venvPython = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $venvPython)) { & $pythonCommand.Source @pythonArgs -m venv $venv }
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) { throw 'No se pudo preparar el entorno virtual de ALLEN.' }
Write-Host '[3/6] Entorno virtual: OK' -ForegroundColor Green
if ($SkipDependencies) { Write-Host '[4/6] Dependencias omitidas por parámetro de prueba.' -ForegroundColor Yellow }
else {
  & $venvPython -m pip install --disable-pip-version-check -r (Join-Path $target 'requirements.txt')
  if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias en el entorno de destino. Comprueba Internet o un índice local.' }
  & $venvPython -c "from importlib.metadata import version; assert version('fastapi')=='0.136.3'; assert version('uvicorn')=='0.49.0'; assert version('httpx')=='0.28.1'; assert version('qrcode')=='8.2'"
  if ($LASTEXITCODE -ne 0) { throw 'Las dependencias instaladas no coinciden con las versiones fijadas.' }
  Write-Host '[4/6] Dependencias Python: OK' -ForegroundColor Green
}

$modelConfig = Join-Path $env:LOCALAPPDATA 'ALLEN\local_model.json'
$configuredExecutable = $null
$configuredModel = $null
if (Test-Path $modelConfig) {
  try {
    $config = Get-Content $modelConfig -Raw | ConvertFrom-Json
    $configuredExecutable = [string]$config.executable
    $configuredModel = [string]$config.model
  } catch { Write-Warning 'local_model.json no es válido; revísalo antes de usar la IA local.' }
}
$llamaCommand = Get-Command llama-server -ErrorAction SilentlyContinue
$llamaExists = ($llamaCommand -and (Test-Path $llamaCommand.Source)) -or ($configuredExecutable -and (Test-Path $configuredExecutable))
if ($llamaCommand -and (Test-Path $llamaCommand.Source)) { $configuredExecutable = $llamaCommand.Source }
if (-not $llamaExists -and $InstallLlamaCpp) {
  $winget = Get-Command winget -ErrorAction SilentlyContinue
  if (-not $winget) { throw 'Motor de IA local no encontrado y winget no está disponible. Instala llama.cpp desde una fuente confiable y configura local_model.json.' }
  Write-Host 'Instalando llama.cpp desde el origen configurado de WinGet...' -ForegroundColor Yellow
  & $winget.Source install --id ggml.llamacpp --exact --accept-source-agreements --accept-package-agreements
  if ($LASTEXITCODE -ne 0) { throw 'WinGet no pudo instalar llama.cpp. ALLEN conserva su instalación; instala llama.cpp desde una fuente confiable y vuelve a ejecutar.' }
  $llamaCommand = Get-Command llama-server -ErrorAction SilentlyContinue
  $llamaExists = [bool]$llamaCommand
}
if (-not $llamaExists) {
  $wingetPackages = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'
  if (Test-Path $wingetPackages) {
    $installedBinary = Get-ChildItem $wingetPackages -Directory -Filter 'ggml.llamacpp*' | ForEach-Object { Get-ChildItem $_.FullName -Filter 'llama-server.exe' -File -Recurse -ErrorAction SilentlyContinue } | Select-Object -First 1
    if ($installedBinary) { $configuredExecutable=$installedBinary.FullName; $llamaExists=$true }
  }
}
if ($llamaExists) { Write-Host '[5/6] llama-server: OK' -ForegroundColor Green }
elseif (-not $SkipDependencies) { throw 'No se encontró llama-server. Ejecuta Instalar_ALLEN.bat y acepta la instalación desde WinGet, o instala llama.cpp manualmente.' }
else { Write-Warning 'llama-server no encontrado en esta prueba de copia.' }

$modelExists = $configuredModel -and (Test-Path $configuredModel -PathType Leaf)
if (-not $modelExists) {
  $hfRoots = @()
  if ($env:LLAMA_CACHE) { $hfRoots += $env:LLAMA_CACHE }
  if ($env:HF_HUB_CACHE) { $hfRoots += $env:HF_HUB_CACHE }
  if ($env:HF_HOME) { $hfRoots += (Join-Path $env:HF_HOME 'hub') }
  $hfRoots += (Join-Path $env:USERPROFILE '.cache\huggingface\hub')
  foreach ($hfRoot in $hfRoots) {
    $snapshot = Join-Path $hfRoot 'models--ggml-org--Qwen3.5-0.8B-GGUF\snapshots'
    if (Test-Path $snapshot) {
      $cachedFile = Get-ChildItem $snapshot -Filter 'Qwen3.5-0.8B*.gguf' -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
      if ($cachedFile) { $configuredModel=$cachedFile.FullName; $modelExists=$true; break }
    }
  }
}
if ($configuredExecutable -and $configuredModel -and ($modelExists -or -not (Test-Path $modelConfig))) {
  New-Item -ItemType Directory -Force -Path (Split-Path $modelConfig) | Out-Null
  @{executable=$configuredExecutable;model=$configuredModel} | ConvertTo-Json | Set-Content -LiteralPath $modelConfig -Encoding utf8
}
if ($modelExists) {
  $modelItem = Get-Item $configuredModel
  $modelDrive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($configuredModel).Substring(0,1))
  Write-Host "Modelo detectado: $($modelItem.Name), $([math]::Round($modelItem.Length / 1GB, 2)) GiB; libre: $([math]::Round($modelDrive.Free / 1GB, 1)) GiB." -ForegroundColor Green
} else {
  Write-Warning 'El modelo de inteligencia artificial de ALLEN todavía no está instalado o no está configurado.'
  Write-Host 'La IA requiere un archivo GGUF local; el instalador puede descargar el modelo Qwen3.5-0.8B-Q8_0 tras tu confirmación.'
}
if (-not $modelExists) {
  $cacheModel = Join-Path $env:USERPROFILE '.cache\huggingface\hub\models--ggml-org--Qwen3.5-0.8B-GGUF\snapshots'
  if (Test-Path $cacheModel) {
    Get-ChildItem $cacheModel -Filter '*.gguf' -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 | ForEach-Object {
      $approx = [math]::Round($_.Length / 1GB, 2)
      Write-Host "Modelo en caché encontrado: $($_.Name), $approx GiB. La configuración debe apuntar a: $($_.FullName)"
    }
  }
  if (-not $SkipDependencies -and $llamaExists) {
    Write-Host 'ALLEN necesita instalar su modelo de inteligencia artificial local.' -ForegroundColor Yellow
    Write-Host 'Modelo: Qwen3.5-0.8B-Q8_0 (~0,78 GiB). Esta descarga desde Hugging Face se realiza una sola vez.'
    $answer = Read-Host '¿Deseas instalarlo ahora? [S/N]'
    if ($answer -match '^(S|SI|SÍ)$') {
      $statusPath = Join-Path $env:TEMP ('allen-install-ai-' + [guid]::NewGuid().ToString('N') + '.txt')
      & $venvPython (Join-Path $target 'start_local_ai.py') --install-model --timeout 7200 --status-file $statusPath
      if ($LASTEXITCODE -ne 0) { throw 'No se pudo descargar o verificar el modelo. Consulta logs\launcher.log y logs\llama-server.log.' }
      if ((Get-Content $statusPath -Raw).Trim() -ne 'ready') { throw 'El modelo no pasó el health check y la inferencia real.' }
      Remove-Item $statusPath -Force -ErrorAction SilentlyContinue
      $config = Get-Content $modelConfig -Raw | ConvertFrom-Json
      $configuredExecutable = [string]$config.executable
      $configuredModel = [string]$config.model
      $modelExists = Test-Path $configuredModel -PathType Leaf
    } else {
      throw 'Instalación incompleta: instala el modelo para iniciar la IA real y vuelve a ejecutar Instalar_ALLEN.bat.'
    }
  }
}

if (Test-Path (Join-Path $target '.allen_initialized')) { Write-Host '[6/6] Instalación actualizada.' -ForegroundColor Green }
Copy-Item (Join-Path $target 'start_allen.bat') (Join-Path $target 'Iniciar_ALLEN.bat') -Force
Copy-Item (Join-Path $target 'install_allen.bat') (Join-Path $target 'Instalar_ALLEN.bat') -Force
if (-not $SkipDependencies -and $target -eq [IO.Path]::GetFullPath("$env:LOCALAPPDATA\ALLEN\app")) {
  try {
    $shortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'ALLEN.lnk'
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = Join-Path $target 'Iniciar_ALLEN.bat'
    $shortcut.WorkingDirectory = $target
    $shortcut.Description = 'Iniciar ALLEN en este equipo'
    $icon = Join-Path $target 'frontend\assets\allen.ico'
    if (Test-Path $icon) { $shortcut.IconLocation = $icon }
    $shortcut.Save()
    Write-Host 'Acceso directo ALLEN creado en el escritorio.'
  } catch { Write-Warning 'No se pudo crear el acceso directo; usa Iniciar_ALLEN.bat en la carpeta de instalación.' }
}
if (-not $SkipDependencies) {
  $statusPath = Join-Path $env:TEMP ('allen-install-ready-' + [guid]::NewGuid().ToString('N') + '.txt')
  & $venvPython (Join-Path $target 'start_local_ai.py') --status-file $statusPath
  if ($LASTEXITCODE -ne 0 -or (Get-Content $statusPath -Raw).Trim() -ne 'ready') { throw 'La IA local no superó health check e inferencia. Revisa los logs.' }
  & $venvPython (Join-Path $target 'scripts\allen_launcher.py') --ai-status $statusPath --no-open
  if ($LASTEXITCODE -ne 0) { throw 'El backend de ALLEN no superó /api/health. Revisa logs\launcher.log.' }
  Remove-Item $statusPath -Force -ErrorAction SilentlyContinue
  Set-Content -LiteralPath (Join-Path $target '.allen_initialized') -Value (Get-Date -Format o) -Encoding ascii
  Write-Host '[6/6] Instalación, modelo, inferencia y backend verificados.' -ForegroundColor Green
  Write-Host '========================================' -ForegroundColor Cyan
  Write-Host '          ALLEN ESTÁ LISTO' -ForegroundColor Cyan
  Write-Host 'Motor IA: instalado · Modelo: Qwen3.5-0.8B · Inferencia: comprobada · Backend: listo' -ForegroundColor Green
  Write-Host 'Para iniciar otra vez: Iniciar_ALLEN.bat' -ForegroundColor Cyan
} else {
  Write-Host "Copia de instalación preparada: $target" -ForegroundColor Cyan
}
