import { defineConfig } from '@playwright/test'

import { fixtureRoot } from './test-utils/fixture-repo'

const PORT = 8779

// The port and the throwaway repository keep these specs away from the board a person has open on the real repository.
export default defineConfig({
  testDir: 'tests',
  // In this order: layout runs before any spec connects a chat, and the e2e tier puts the fixture back for the story actions.
  projects: [
    { name: 'layout', testMatch: 'board-surface.spec.ts' },
    { name: 'playwright-tier', testMatch: '**/*.behavior.playwright.ts' },
    { name: 'e2e-tier', testMatch: '**/*.behavior.e2e.ts' },
    { name: 'story-actions', testMatch: 'story-actions.spec.ts' },
  ],
  workers: 1,
  timeout: 30_000,
  expect: { timeout: 8_000 },
  reporter: 'list',
  use: { baseURL: `http://127.0.0.1:${PORT}`, viewport: { width: 1600, height: 900 } },
  webServer: {
    command: 'npx tsx test-utils/fixture-repo.ts && npm run build && npx tsx packages/session-board/serve.ts',
    url: `http://127.0.0.1:${PORT}/api/chats`,
    reuseExistingServer: false,
    timeout: 120_000,
    env: { BOARD_PORT: String(PORT), BOARD_PROJECT: fixtureRoot, BOARD_FIXTURE_ROOT: fixtureRoot },
  },
})
