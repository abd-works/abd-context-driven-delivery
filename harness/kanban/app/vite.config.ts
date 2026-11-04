import { fileURLToPath } from 'node:url'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const resolved = (path: string): string => fileURLToPath(new URL(path, import.meta.url))

export const aliases = {
  '@src': resolved('./src'),
  '@cdd': resolved('../../../.claude/language-adapters/typescript'),
  // The generated views sit outside this package, so they reach React through this application's own copy.
  react: resolved('./node_modules/react'),
  'test-utils': resolved('./test-utils'),
}

export default defineConfig({ plugins: [react()], resolve: { alias: aliases }, build: { outDir: 'dist' } })
