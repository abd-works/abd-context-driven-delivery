# One-time / repeat bootstrap for abd-context-driven-delivery tools on Windows.
# Usage (from repo root): .\setup.ps1
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"

function Find-SystemPython {
    foreach ($version in @("-3.12", "-3.13", "-3.14", "-3")) {
        try {
            $exe = & py $version -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $exe -and (Test-Path $exe.Trim())) {
                return $exe.Trim()
            }
        } catch {}
    }
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python314-arm64\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313-arm64\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312-arm64\python.exe"
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
& $VenvPython -c "import sys; from pathlib import Path; root = Path(r'$Root'); sys.path.insert(0, str(root / 'primitives')); from tools.repo_paths import write_venv_pth; write_venv_pth(root / '.venv', root)"
try {
    $ErrorActionPreference = "Continue"
    & $VenvPython -m pip install -e $Root *>&1 | Out-Null
} catch {
} finally {
    $ErrorActionPreference = "Stop"
}
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Editable install skipped (optional). Tools work via .\tools.ps1 and abd_cdd_paths.pth."
}
Write-Host "Ready. Use: .\tools.ps1 manifest <toolset>"
