import { fileURLToPath } from 'node:url'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// The app's ports, written once for this config, its server, and the Python that reports and starts the app.
import ports from './ports.json'

const resolved = (path: string): string => fileURLToPath(new URL(path, import.meta.url))

// The generated CDD classes sit in the install, and the graph explorer's source view in the Graph app's folder, both
// outside this package, so they take React and Monaco from here.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@cdd': resolved('../../../../.claude/language-adapters/typescript'),
      '@source-view': resolved('../../../../harness/graph/app/source'),
      react: resolved('./node_modules/react'),
      'react-dom': resolved('./node_modules/react-dom'),
      '@monaco-editor/react': resolved('./node_modules/@monaco-editor/react'),
      'monaco-editor': resolved('./node_modules/monaco-editor'),
    },
  },
  build: { outDir: 'dist', emptyOutDir: true },
  server: { proxy: { '/api': `http://127.0.0.1:${ports.files[0]}` } },
  test: { environment: 'jsdom' },
})
