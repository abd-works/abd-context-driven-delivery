---
scanner: test_scripts_scanner.py
---

# Rule: Scaffold Test Runner Scripts

Every generated MERN project must include a `scripts/` folder at the workspace root with shell scripts that invoke each test tier. These scripts make test commands discoverable, CI-friendly, and runnable without knowing npm script names.

## Required Scripts

| File | Tier | Requires |
|------|------|---------|
| `scripts/test.sh` | Server + client unit/component tests (Vitest) | Node.js only |
| `scripts/test.ps1` | Same — Windows equivalent | Node.js only |
| `scripts/test-e2e.sh` | End-to-end browser tests (Playwright) | `packages/app-client` serving the React frontend |
| `scripts/test-e2e.ps1` | Same — Windows equivalent | `packages/app-client` serving the React frontend |

**`test.sh` / `test.ps1` do NOT run E2E tests.** They run Vitest only — server and client unit/component tests. This is intentional: E2E tests require a live frontend and are a separate step.

**`test-e2e.sh` / `test-e2e.ps1` require `packages/app-client` to exist and be wired into `playwright.config.ts`.** Without a running React frontend, every Playwright test will fail with `Cannot GET /<route>` because the page routes (`/products/:sku`, `/store-locator`, etc.) only exist when a frontend app is serving them. The API routes (`/api/...`) are not the same as page routes.

## Script Contents

### `scripts/test.sh`

```bash
#!/usr/bin/env bash
# Runs server and client unit/component tests ONLY (Vitest).
# Does NOT run E2E tests. Use scripts/test-e2e.sh for end-to-end tests.
set -euo pipefail
cd "$(dirname "$0")/.."
npx vitest run
```

### `scripts/test.ps1`

```powershell
# Runs server and client unit/component tests ONLY (Vitest).
# Does NOT run E2E tests. Use scripts/test-e2e.ps1 for end-to-end tests.
Set-Location (Split-Path -Parent $PSScriptRoot)
npx vitest run
```

### `scripts/test-e2e.sh`

```bash
#!/usr/bin/env bash
# Runs Playwright end-to-end tests.
#
# REQUIRES: packages/app-client must exist and serve the React frontend.
# Without it, page routes like /products/:sku do not exist and every test
# will fail with "Cannot GET /<route>".
set -euo pipefail
cd "$(dirname "$0")/.."
npx playwright test
```

### `scripts/test-e2e.ps1`

```powershell
# Runs Playwright end-to-end tests.
#
# REQUIRES: packages/app-client must exist and serve the React frontend.
# Without it, page routes like /products/:sku do not exist and every test
# will fail with "Cannot GET /<route>".
Set-Location (Split-Path -Parent $PSScriptRoot)
npx playwright test
```

The `playwright.config.ts` `webServer` block starts the Express API server automatically. The React frontend must also be wired into `webServer` (as a second entry) before E2E tests can pass.

## DO

- Create all four scripts every time a new project is scaffolded.
- Make `.sh` scripts executable: `git update-index --chmod=+x scripts/test.sh scripts/test-e2e.sh`.
- Keep scripts thin — they `cd` to the workspace root and delegate to `npx`; no test logic lives in the script.
- Include `set -euo pipefail` in `.sh` scripts so failures surface immediately.
- Include the `# REQUIRES:` comment in both `test-e2e` scripts so developers know what must exist before running them.
- Add both the API server **and** the React frontend as `webServer` entries in `playwright.config.ts` before claiming E2E tests are runnable.

```typescript
// playwright.config.ts — CORRECT: both servers declared
webServer: [
  {
    command: 'node --import tsx/esm packages/app-server/dev.ts',
    url: 'http://localhost:3001/health',
    reuseExistingServer: true,
  },
  {
    command: 'npx vite packages/app-client',
    url: 'http://localhost:3000',
    reuseExistingServer: true,
  },
],
```

## DON'T

- Omit the `# REQUIRES:` comment from the `test-e2e` scripts.
- Omit either platform's scripts — teams on Windows need `.ps1`; teams on Mac/Linux need `.sh`.
- Hard-code absolute paths in scripts — always navigate relative to the script's own location.
- Claim that E2E tests are complete or passing just because the `*_e2e.spec.ts` files compile and list with `--list`. **Spec files existing ≠ E2E tests passing.** They need a live frontend serving real page routes.
- Generate `test-e2e.sh` without first verifying `packages/app-client` exists and is wired into `playwright.config.ts`.

```bash
# WRONG — no warning, developer has no idea why every test fails
#!/usr/bin/env bash
npx playwright test
```
