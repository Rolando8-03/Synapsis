param([string]$Instalador = "build/windows/Synapsis-Setup.exe")
$ErrorActionPreference = "Stop"
$Installer = (Resolve-Path $Instalador).Path
$Root = Join-Path $env:LOCALAPPDATA "Programs/Synapsis"
$Shortcut = Join-Path ([Environment]::GetFolderPath("Programs")) "Synapsis.lnk"
$Registry = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{472314BD-21AB-4D13-92E3-2E2BA6CB3639}_is1'
if ((Test-Path $Root) -or (Test-Path $Shortcut) -or (Test-Path $Registry)) {
    throw "Ejecutá esta prueba de instalación en un usuario de pruebas sin Synapsis instalado."
}
function Run-Setup($Path) {
    $Result = Start-Process -FilePath $Path -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART' -Wait -PassThru
    if ($Result.ExitCode) { throw "El proceso $Path devolvió $($Result.ExitCode)." }
}
try {
    Run-Setup $Installer
    $Entry = Get-ItemProperty $Registry
    $Version = (Get-Content -Raw plataformas/VERSION).Trim()
    if ($Entry.DisplayName -notmatch '^Synapsis( |$)' -or $Entry.DisplayVersion -ne $Version -or !$Entry.DisplayIcon) {
        throw 'La entrada de Aplicaciones instaladas no tiene el nombre, la versión o el icono esperado.'
    }
    if (!(Test-Path $Shortcut)) { throw 'Falta el acceso directo del menú Inicio.' }
    $Link = (New-Object -ComObject WScript.Shell).CreateShortcut($Shortcut)
    if ($Link.TargetPath -ne (Join-Path $Root "Synapsis.exe")) { throw 'El acceso directo apunta a otro ejecutable.' }
    python -m plataformas.windows.verificar $Link.TargetPath
    if ($LASTEXITCODE) { throw 'Falló la comprobación desde la ruta instalada.' }
    Run-Setup $Installer
    if (!(Test-Path $Link.TargetPath) -or !(Test-Path $Shortcut)) { throw 'Falló la reinstalación.' }
} finally {
    $Uninstaller = Join-Path $Root 'unins000.exe'
    if (Test-Path $Uninstaller) { Run-Setup $Uninstaller }
}
if ((Test-Path (Join-Path $Root 'Synapsis.exe')) -or (Test-Path $Shortcut) -or (Test-Path $Registry)) {
    throw 'La desinstalación no retiró Synapsis de Windows.'
}
