# One-time / repeat bootstrap for abd-context-driven-delivery tools on Windows.
# Usage (from repo root): .\setup.ps1
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"

function Find-SystemPython {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    throw "No system Python found. Install Python 3.12+ or create .venv manually."
}

if (-not (Test-Path $VenvPython)) {
    $SystemPython = Find-SystemPython
    & $SystemPython -m venv (Join-Path $Root ".venv")
}

$env:PYTHONIOENCODING = "utf-8"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $Root "requirements.txt")
& $VenvPython -m pip install -e $Root
Write-Host "Ready. Use: .\tools.ps1 manifest <toolset>"
