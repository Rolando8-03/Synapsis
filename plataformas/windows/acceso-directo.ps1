param([string]$RutaPythonw)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
if (-not $RutaPythonw) {
    $RutaPythonw = Join-Path $Root ".venv/Scripts/pythonw.exe"
    if (-not (Test-Path $RutaPythonw)) { $RutaPythonw = (Get-Command pythonw.exe -ErrorAction Stop).Source }
}
$RutaPythonw = (Resolve-Path $RutaPythonw).Path
$Desktop = [Environment]::GetFolderPath("Desktop")
$Path = Join-Path $Desktop "Synapsis (Python).lnk"
$Shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($Path)
$Shortcut.TargetPath = $RutaPythonw
$Shortcut.Arguments = '"' + (Join-Path $Root "abrir.py") + '"'
$Shortcut.WorkingDirectory = $Root
$Shortcut.Description = "Abrir Synapsis sin consola"
$Shortcut.Save()
Write-Output $Path
