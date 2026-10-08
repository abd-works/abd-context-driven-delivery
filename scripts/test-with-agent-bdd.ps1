# Vanilla suite first (story tests + mamba specs), then agentic BDD.
$ErrorActionPreference = "Continue"
$vanilla = Join-Path $PSScriptRoot "test.ps1"

& $vanilla -Suite vanilla
$vanillaExit = $LASTEXITCODE

& $vanilla -Suite agent
$agentExit = $LASTEXITCODE

Write-Host ""
if ($vanillaExit -eq 0) { Write-Host "vanilla suite passed" } else { Write-Host "vanilla suite failed" }
if ($agentExit -eq 0) { Write-Host "agentic BDD passed" } else { Write-Host "agentic BDD failed" }

if ($vanillaExit -ne 0 -or $agentExit -ne 0) { exit 1 }
exit 0
