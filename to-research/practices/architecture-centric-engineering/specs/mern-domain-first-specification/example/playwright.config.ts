import { defineConfig } from '@playwright/test';

export default defineConfig({
  testMatch: '**/*_e2e.spec.ts',
  use: { baseURL: 'http://localhost:3000' },
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
});
