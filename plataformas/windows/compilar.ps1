param(
    [string]$Version,
    [string]$Salida = "build/windows",
    [string]$Python = "python",
    [switch]$SoloEjecutable
)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
if (-not $Version) { $Version = (Get-Content -Raw (Join-Path $Root "plataformas/VERSION")).Trim() }
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "La versión debe usar el formato X.Y.Z." }
if (-not [System.IO.Path]::IsPathRooted($Salida)) { $Salida = Join-Path $Root $Salida }
$Salida = [System.IO.Path]::GetFullPath($Salida)
if (Test-Path $Salida) { throw "La carpeta de salida ya existe. Elegí una carpeta nueva." }
New-Item -ItemType Directory -Path $Salida | Out-Null
$env:QT_QPA_PLATFORM = "offscreen"
$Icon = Join-Path $Salida "Synapsis.ico"
& $Python (Join-Path $PSScriptRoot "icono.py") $Icon
if ($LASTEXITCODE) { throw "No se pudo generar el icono." }
Push-Location $Root
try {
    $UI = Join-Path $Root "dist"
    $Legacy = Join-Path $Root "motor_grupo4"
    $LegacyPython = Join-Path $Legacy "python"
    & $Python -m PyInstaller --noconfirm --onedir --windowed --name Synapsis --icon $Icon `
        --add-data "$UI;dist" --paths $Legacy --paths $LegacyPython --exclude-module scipy `
        --distpath (Join-Path $Salida "bin") --workpath (Join-Path $Salida "temp") `
        --specpath $Salida abrir.py
    if ($LASTEXITCODE) { throw "Falló PyInstaller." }
} finally {
    Pop-Location
}
$Files = Join-Path $Salida "bin/Synapsis"
$BundledModules = & $Python -m PyInstaller.utils.cliutils.archive_viewer -r -b (Join-Path $Files 'Synapsis.exe')
if ($LASTEXITCODE) { throw 'No se pudo inspeccionar el paquete Python.' }
$BundledModules = $BundledModules | ForEach-Object { $_.Trim() }
foreach ($Module in @('entrada_datos', 'analisis_sistema', 'operaciones_matrices', 'relaciones_vectoriales', 'calculo_basico', 'formato_latex')) {
    if ($BundledModules -notcontains $Module) { throw "Falta el módulo $Module en el ejecutable." }
}
foreach ($Asset in @("Synapsis.exe", "_internal/dist/index.html", "_internal/dist/vendor/mathlive/mathlive.min.mjs")) {
    if (-not (Test-Path (Join-Path $Files $Asset))) { throw "Falta $Asset en el paquete." }
}
if (-not (Get-ChildItem $Files -Recurse -Filter QtWebEngineProcess.exe)) { throw "Falta QtWebEngineProcess.exe." }
Compress-Archive -CompressionLevel Fastest -Path $Files -DestinationPath (Join-Path $Salida "Synapsis-Windows-x64.zip")
if (-not $SoloEjecutable) {
    $ISCC = (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source
    if (-not $ISCC) { $ISCC = Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6/ISCC.exe" }
    if (-not (Test-Path $ISCC)) { throw "Instalá Inno Setup 6 para generar Synapsis-Setup.exe." }
    & $ISCC "/DAppVersion=$Version" "/DBuildDir=$Salida" "/DFilesDir=$Files" (Join-Path $PSScriptRoot "Synapsis.iss")
    if ($LASTEXITCODE) { throw "Falló Inno Setup." }
}
