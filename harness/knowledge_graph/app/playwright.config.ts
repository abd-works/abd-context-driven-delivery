import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*_e2e.spec.ts',
  webServer: [
    {
      command: 'npm run dev:server --workspace=@cdd/explore-knowledge-graph',
      port: 3001,
      reuseExistingServer: true,
    },
    {
      command: 'npm run dev --workspace=@cdd/explore-knowledge-graph',
      port: 3000,
      reuseExistingServer: true,
    },
  ],
  use: {
    ...devices['Desktop Chrome'],
    baseURL: 'http://localhost:3000',
  },
});
