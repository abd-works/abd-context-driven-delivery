# Run python -m tools against this checkout (venv + UTF-8 + PYTHONPATH).
# Usage (from repo root): .\tools.ps1 manifest <toolset>
#                         .\tools.ps1 run _req.yaml
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "No venv at $VenvPython. Run .\setup.ps1 first."
}
$env:PYTHONIOENCODING = "utf-8"
$parts = @(
    $Root
    (Join-Path $Root "primitives")
    (Join-Path $Root "utilities")
    (Join-Path $Root "context_tools")
    (Join-Path $Root "context_tools\actions")
)
$env:PYTHONPATH = ($parts -join [IO.Path]::PathSeparator)
& $VenvPython -m tools @args
exit $LASTEXITCODE
