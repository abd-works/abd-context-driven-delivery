import { rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { defineConfig } from '@playwright/test'

import { fixtureRoot } from './test-utils/fixture-repo'

const PORT = 8779
// The specs' chats live apart from the person's real ones, which the cdd-board mod in each chat keeps under ~/.claude.
const CHATS_FOLDER = join(tmpdir(), 'cdd-board-surface-chats')
const CLAUDE_PROJECTS = join(tmpdir(), 'cdd-board-surface-projects')
// A command left waiting by an earlier run would reach this run's chat, so each run starts with no chats.
rmSync(CHATS_FOLDER, { recursive: true, force: true })

// The port and the throwaway repository keep these specs away from the board a person has open on the real repository.
export default defineConfig({
  testDir: 'tests',
  // In this order: layout runs before any spec connects a chat, and the e2e tier puts the fixture back for the story actions.
  projects: [
    { name: 'layout', testMatch: 'board-surface.spec.ts' },
    { name: 'e2e-tier', testMatch: '**/*.behavior.e2e.ts' },
    { name: 'story-actions', testMatch: 'story-actions.spec.ts' },
    { name: 'story-ui', testDir: '..', testMatch: '*.story.ui.spec.ts' },
  ],
  workers: 1,
  timeout: 30_000,
  expect: { timeout: 8_000 },
  reporter: 'list',
  use: { baseURL: `http://127.0.0.1:${PORT}`, viewport: { width: 1600, height: 900 } },
  webServer: {
    command: 'npx tsx test-utils/fixture-repo.ts && npm run build && npx tsx packages/session-board/serve.ts',
    url: `http://127.0.0.1:${PORT}/`,
    reuseExistingServer: false,
    timeout: 120_000,
    env: { BOARD_PORT: String(PORT), BOARD_PROJECT: fixtureRoot, BOARD_FIXTURE_ROOT: fixtureRoot, CDD_CHATS_FOLDER: CHATS_FOLDER, CDD_CLAUDE_PROJECTS: CLAUDE_PROJECTS },
  },
})
