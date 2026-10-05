
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "==> Creating virtual environment"
    if (Get-Command py -ErrorAction SilentlyContinue) { py -3 -m venv .venv } else { python -m venv .venv }
    if ($LASTEXITCODE) { throw "Could not create venv. Is Python 3.10+ installed?" }
}
$py = ".venv\Scripts\python.exe"

Write-Host "==> Installing build tools"
& $py -m pip install -q -e ".[build]"
if ($LASTEXITCODE) { throw "pip install failed" }

Write-Host "==> Building executable"
& $py scripts\build.py
if ($LASTEXITCODE) { throw "Build failed" }

$dest = Join-Path $env:LOCALAPPDATA "Programs\Redox"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item "dist\redox.exe" $dest -Force
Write-Host "==> Installed: $dest\redox.exe"

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }
if (($userPath -split ";") -notcontains $dest) {
    [Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(";") + ";" + $dest).TrimStart(";"), "User")
    Write-Host "Added $dest to your PATH. Open a NEW terminal, then run 'redox'."
} else {
    Write-Host "Done! Run 'redox' to start."
}
