import { defineConfig } from 'vitest/config';

// Vitest runs *_server.test.ts and *_client.test.tsx only — excludes *_e2e.spec.ts (Playwright).
export default defineConfig({
  test: {
    include: ['tests/**/*_server.test.ts', 'tests/**/*_client.test.tsx'],
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
});
