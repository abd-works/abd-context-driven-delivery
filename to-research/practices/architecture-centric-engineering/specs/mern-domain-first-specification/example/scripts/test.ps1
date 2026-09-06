# Runs server and client unit/component tests ONLY (Vitest).
# Does NOT run E2E tests. Use scripts/test-e2e.ps1 for end-to-end tests.
Set-Location (Split-Path -Parent $PSScriptRoot)
npx vitest run
