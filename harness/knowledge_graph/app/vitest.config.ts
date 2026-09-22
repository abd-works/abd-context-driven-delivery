import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    include: ['tests/**/*_server.test.ts', 'tests/**/*_client.test.tsx'],
    exclude: ['tests/**/*_e2e.spec.ts', '**/node_modules/**'],
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
});
