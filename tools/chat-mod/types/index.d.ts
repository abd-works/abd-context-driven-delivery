// ServerHealthData comes from the language adapter, generated from what ServerHealth.to_json() returns.
// The rest is what the server health band keeps for itself between draws.
import type { ServerHealthData } from '@cdd/harness/health/server_health'

export type ServerHealthJson = {
  connection: 'connected' | 'reconnecting' | 'disconnected' | 'tools-missing'
  report: ServerHealthData | null
  toolCount: number
  problem: string | null
  attempt: number
  isRestored: boolean
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
