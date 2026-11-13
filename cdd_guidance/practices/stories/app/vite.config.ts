import { fileURLToPath } from 'node:url'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

import { STORY_MAP_PAGE } from './story-map-page'

const resolved = (path: string): string => fileURLToPath(new URL(path, import.meta.url))

// The board's server, which serves this page at /story-map and answers its /api calls (space/kanban's ports.json).
const BOARD = 'http://127.0.0.1:8778'

// The generated story map classes sit in the install, outside this package, so they take React from here.
export default defineConfig({
  base: `${STORY_MAP_PAGE}/`,
  plugins: [react()],
  resolve: {
    alias: {
      '@cdd': resolved('../../../../.claude/language-adapters/typescript'),
      react: resolved('./node_modules/react'),
      '@monaco-editor/react': resolved('./node_modules/@monaco-editor/react'),
    },
  },
  build: { outDir: 'dist', emptyOutDir: true },
  server: { proxy: { '/api': BOARD } },
  test: { environment: 'jsdom' },
})
