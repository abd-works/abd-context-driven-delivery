$repo = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $repo ".venv\Scripts\python.exe"
$python = if (Test-Path $venv) { $venv } else { "python" }
& $python (Join-Path $PSScriptRoot "start_graph_app.py") @args
exit $LASTEXITCODE
