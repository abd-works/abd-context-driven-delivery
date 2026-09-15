# Run python -m tools against this checkout (venv + UTF-8 + PYTHONPATH).
# Usage (from repo root): .\tools.ps1 manifest <toolset>
#                         .\tools.ps1 run -   (pipe the YAML fence; stdin is forwarded)
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

function Import-DotEnvFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    foreach ($raw in Get-Content -LiteralPath $Path) {
        $line = $raw.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) { continue }
        $eq = $line.IndexOf("=")
        $key = $line.Substring(0, $eq).Trim()
        $value = $line.Substring($eq + 1).Trim()
        if (
            ($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))
        ) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        if ($key -eq "SECRETS_IMPORT") {
            foreach ($item in ($value -split ",")) {
                $importPath = $item.Trim()
                if ($importPath) { Import-DotEnvFile $importPath }
            }
            continue
        }
        if ($key -and $value -and -not [Environment]::GetEnvironmentVariable($key)) {
            Set-Item -Path "Env:$key" -Value $value
        }
    }
}

$kitSecrets = Join-Path $Root "conf\.secrets"
Import-DotEnvFile $kitSecrets
Import-DotEnvFile (Join-Path $Root "conf\.env")
if ($env:CDD_SECRETS_FILE) { Import-DotEnvFile $env:CDD_SECRETS_FILE }
$answersSecrets = Join-Path (Split-Path $Root -Parent) "abd-works-repo\abd-answers\conf\.secrets"
Import-DotEnvFile $answersSecrets
if ($MyInvocation.ExpectingInput) {
    $input | & $VenvPython -m tools @args
} else {
    & $VenvPython -m tools @args
}
exit $LASTEXITCODE
