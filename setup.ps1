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

$RequirementsPath = Join-Path $Root "requirements.txt"
$RequirementsBody = @"
# Runtime and test deps for this checkout (install into .venv via setup.ps1).
# Keep in sync with [project].dependencies in pyproject.toml plus the test runner.
expects>=0.9.0
PyYAML>=6.0
mcp==1.30.0
numpy>=1.26
faiss-cpu>=1.8.0
openai>=1.40.0
anyio>=4.5
httpx>=0.27.1
httpx-sse>=0.4
jsonschema>=4.20.0
pydantic>=2.11.0
pydantic-settings>=2.5.2
pyjwt>=2.10.1
python-multipart>=0.0.9
pywin32>=310; sys_platform == 'win32'
sse-starlette>=1.6.1
starlette>=0.27
typing-extensions>=4.9.0
typing-inspection>=0.4.1
uvicorn>=0.31.1
mamba>=0.11.3
"@
if (-not (Test-Path $RequirementsPath)) {
    Set-Content -LiteralPath $RequirementsPath -Value $RequirementsBody -Encoding utf8
    Write-Host "Wrote $RequirementsPath"
}

$env:PYTHONIOENCODING = "utf-8"
& $VenvPython -m pip install --upgrade pip
$Missing = & $VenvPython -c @"
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version
text = Path(r'$RequirementsPath').read_text(encoding='utf-8')
missing = []
for raw in text.splitlines():
    line = raw.split('#', 1)[0].strip()
    if not line:
        continue
    req = line.split(';', 1)[0].strip()
    name = req.split('[', 1)[0]
    for sep in ('==', '>=', '<=', '~=', '!=', '>', '<'):
        if sep in name:
            name = name.split(sep, 1)[0]
            break
    name = name.strip()
    if not name:
        continue
    try:
        version(name)
    except PackageNotFoundError:
        missing.append(name)
print('\n'.join(missing))
"@
if ($LASTEXITCODE -ne 0) {
    throw "Could not check installed packages against requirements.txt"
}
if ("$Missing".Trim()) {
    Write-Host "Installing missing packages: $(($Missing -split '\s+' | Where-Object { $_ }) -join ', ')"
    & $VenvPython -m pip install -r $RequirementsPath
    if ($LASTEXITCODE -ne 0) {
        throw "pip install -r requirements.txt failed"
    }
} else {
    Write-Host "All requirements already installed"
}
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

$parts = @(
    $Root
    (Join-Path $Root "primitives")
    (Join-Path $Root "utilities")
    (Join-Path $Root "context_tools")
    (Join-Path $Root "context_tools\actions")
)
$env:PYTHONPATH = ($parts -join [IO.Path]::PathSeparator)
Write-Host "Deploying harness into this checkout (.cursor)..."
& $VenvPython -m tools run harness.harness:Harness --tool write_deploy --context type=Cursor --context repo_root=$Root --arg mcp=true --arg code_language=python --arg deploy_path=$Root
if ($LASTEXITCODE -ne 0) {
    throw "Harness write_deploy failed"
}
Write-Host "Ready. Use: .\tools.ps1 manifest <toolset>"
# Reaching here means setup succeeded; do not leak the optional step's exit code.
exit 0
