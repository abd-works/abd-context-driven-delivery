$repo = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $repo ".venv\Scripts\python.exe"
$python = if (Test-Path $venv) { $venv } else { "python" }
& $python (Join-Path $PSScriptRoot "ping_hook.py") @args
exit $LASTEXITCODE
