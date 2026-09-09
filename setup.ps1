# One-time / repeat bootstrap for abd-context-driven-delivery tools on Windows.
# Usage (from repo root): .\setup.ps1
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Venv = Join-Path $Root ".venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"

function Test-PythonExe {
    param([string]$Exe)
    $exe = ($Exe -replace '"', "").Trim()
    if (-not $exe -or -not (Test-Path $exe)) { return $false }
    # A venv interpreter must never seed a venv - that is how a foreign home leaks in.
    if ($exe -match "[\\/]\.venv[\\/]") { return $false }
    $prior = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { & $exe -I -c "pass" 2>$null | Out-Null } finally { $ErrorActionPreference = $prior }
    return ($LASTEXITCODE -eq 0)
}

function Find-SystemPython {
    foreach ($version in @("-3.12", "-3.13", "-3.14", "-3")) {
        try {
            $exe = & py $version -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and (Test-PythonExe $exe)) {
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
        "$env:LOCALAPPDATA\Programs\Python\Python312-arm64\python.exe",
        "$env:ProgramFiles\Python314\python.exe",
        "$env:ProgramFiles\Python313\python.exe",
        "$env:ProgramFiles\Python312\python.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-PythonExe $candidate) { return $candidate }
    }
    try {
        foreach ($found in (& where.exe python 2>$null)) {
            if (Test-PythonExe $found) { return $found.Trim() }
        }
    } catch {}
    throw "No system Python found. Install Python 3.12+ or create .venv manually."
}

function Get-VenvProblem {
    if (-not (Test-Path $VenvPython)) { return "no interpreter at $VenvPython" }
    $probe = "import sys; sys.path.insert(0, r'$Root\primitives'); " +
        "from tools.repo_paths import venv_problem; print(venv_problem(r'$Venv', probe=False))"
    $prior = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { $reported = & $VenvPython -c $probe 2>$null } finally { $ErrorActionPreference = $prior }
    if ($LASTEXITCODE -ne 0) { return "$VenvPython does not run (exit $LASTEXITCODE)" }
    return ("$reported").Trim()
}

$Problem = Get-VenvProblem
if ($Problem) {
    if (Test-Path $Venv) { Remove-Item -Recurse -Force $Venv }
    $SystemPython = Find-SystemPython
    & $SystemPython -m venv $Venv
    Write-Host "Rebuilt .venv with $SystemPython - $Problem"
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
# Reaching here means setup succeeded; do not leak the optional step's exit code.
exit 0
