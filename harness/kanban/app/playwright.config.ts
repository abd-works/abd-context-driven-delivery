import { defineConfig } from '@playwright/test'

import { fixtureRoot } from './tests/fixture-repo'

const PORT = 8779

// The port and the throwaway repository keep these specs away from the board a person has open on the real repository.
export default defineConfig({
  testDir: 'tests',
  testMatch: '*.spec.ts',
  workers: 1,
  timeout: 30_000,
  expect: { timeout: 8_000 },
  reporter: 'list',
  use: { baseURL: `http://127.0.0.1:${PORT}`, viewport: { width: 1600, height: 900 } },
  webServer: {
    command: 'npx tsx tests/fixture-repo.ts && npx vite build && npx tsx src/serve.ts',
    url: `http://127.0.0.1:${PORT}/api/chats`,
    reuseExistingServer: false,
    timeout: 120_000,
    env: { BOARD_PORT: String(PORT), BOARD_PROJECT: fixtureRoot, BOARD_FIXTURE_ROOT: fixtureRoot },
  },
})
