import { defineConfig } from 'vitest/config'

import { aliases } from './vite.config'

export default defineConfig({ resolve: { alias: aliases }, test: { include: ['src/**/*.spec.ts'] } })
