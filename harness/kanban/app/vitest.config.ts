import { defineConfig } from 'vitest/config'

import { aliases } from './vite.config'

const SERVER_TIER_MILLISECONDS = 120_000

// The server tier waits on a real cdd server, so a test may take as long as that server does.
export default defineConfig({
  resolve: { alias: aliases },
  test: {
    include: ['src/**/*.spec.ts', 'tests/**/*.behavior.server.spec.ts'],
    testTimeout: SERVER_TIER_MILLISECONDS,
    hookTimeout: SERVER_TIER_MILLISECONDS,
  },
})
