#!/usr/bin/env bash
# Runs Playwright end-to-end tests.
#
# REQUIRES: packages/app-client must exist and serve the React frontend.
# Without it, page routes do not exist and every test will fail with "Cannot GET /<route>".
set -euo pipefail
cd "$(dirname "$0")/.."
npx playwright test
