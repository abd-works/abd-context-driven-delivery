# Runs Playwright end-to-end tests.
#
# REQUIRES: packages/app-client must exist and serve the React frontend.
# Without it, page routes do not exist and every test will fail with "Cannot GET /<route>".
Set-Location (Split-Path -Parent $PSScriptRoot)
npx playwright test
