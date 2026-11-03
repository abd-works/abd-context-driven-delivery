import type { ServerHealthData } from '@cdd/harness/health/server-health'

// What the server health band keeps between draws. The report's shape is the generated ServerHealthData, imported above.
export type ServerHealthJson = {
  connection: 'connected' | 'reconnecting' | 'disconnected' | 'tools-missing'
  report: ServerHealthData | null
  toolCount: number
  problem: string | null
  attempt: number
}

export type HealthViewJson = { isPinned: boolean; areDetailsOpen: boolean }

export type InstallJson = { state: 'idle' | 'running' | 'installed' | 'failed'; error: string | null }

declare module 'claude-code' {
  interface PluginState {
    'cdd-board': {
      serverHealth: ServerHealthJson
      healthView: HealthViewJson
      install: InstallJson
    }
  }
}
