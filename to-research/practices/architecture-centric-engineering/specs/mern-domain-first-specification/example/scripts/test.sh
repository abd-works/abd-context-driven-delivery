#!/usr/bin/env bash
# Runs server and client unit/component tests ONLY (Vitest).
# Does NOT run E2E tests. Use scripts/test-e2e.sh for end-to-end tests.
set -euo pipefail
cd "$(dirname "$0")/.."
npx vitest run
