import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*_story.test.tsx',
  timeout: 15 * 60 * 1000,
  webServer: [
    {
      command: 'npm run dev:server --workspace=@cdd/explore-knowledge-graph',
      port: 3001,
      reuseExistingServer: true,
      timeout: 120_000,
    },
    {
      command: 'npm run dev --workspace=@cdd/explore-knowledge-graph',
      port: 3000,
      reuseExistingServer: true,
      timeout: 120_000,
    },
  ],
  use: {
    ...devices['Desktop Chrome'],
    baseURL: 'http://localhost:3000',
  },
});
