import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    include: ['packages/**/*-behavior.test.ts', 'tests/**/*.test.ts', 'tests/**/*.test.tsx'],
    exclude: ['tests/**/*_e2e.spec.ts', 'tests/**/*_story.test.tsx', '**/node_modules/**'],
    globals: true,
    environment: 'node',
    setupFiles: [],
  },
});
