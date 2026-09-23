# Run the practice hierarchy report (repo root, Clean Engineering + BDD, no populate).
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ReportArgs
)
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
python (Join-Path $PSScriptRoot "write_practice_hierarchy.py") `
    --no-populate `
    --practice clean_engineering `
    --practice bdd `
    @ReportArgs
