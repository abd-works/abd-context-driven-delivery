# Start the persistent CodeQL query daemon for this repository.
$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
foreach ($bin in @(
        (Join-Path $env:LOCALAPPDATA "Programs\codeql\codeql"),
        (Join-Path $env:LOCALAPPDATA "Programs\codeql")
    )) {
    if (Test-Path $bin) {
        $env:PATH = "$bin;$env:PATH"
        break
    }
}
$env:PYTHONPATH = @(
    $Repo
    (Join-Path $Repo "tools")
    (Join-Path $Repo "practices")
    (Join-Path $Repo "actions")
) -join [IO.Path]::PathSeparator
Set-Location $Repo
python -c @"
import sys
from pathlib import Path
repo = Path(r'$Repo')
sys.path.insert(0, str(repo))
import mcp.types
for cat in ('practices', 'tools', 'actions'):
    path = str(repo / cat)
    if path not in sys.path:
        sys.path.insert(0, path)
from harness.mcp.codeql_query_daemon import ensure_query_server
client = ensure_query_server(repo)
print(f'query-server daemon pid={client.pid} port={client.port}')
"@
