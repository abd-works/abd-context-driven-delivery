# Durable entry for python -m tools on Windows.
# Usage (from abd-context-driven-delivery):
#   .\tools.ps1 manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
#   .\tools.ps1 run _req.yaml
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Missing $Python - create the venv and install deps before running tools."
}
$env:PYTHONIOENCODING = "utf-8"
# Belt-and-suspenders: ensure namespace packages resolve even if .pth / editable install is missing.
$env:PYTHONPATH = @(
    $Root,
    (Join-Path $Root "primitives"),
    (Join-Path $Root "utilities"),
    (Join-Path $Root "context_tools"),
    (Join-Path $Root "context_tools\actions")
) -join ";"
& $Python -m tools @args
exit $LASTEXITCODE
