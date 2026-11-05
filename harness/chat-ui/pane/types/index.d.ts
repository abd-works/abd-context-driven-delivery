// `claude plugin validate` holds this contract to one self-contained file, so it imports nothing. Each atom's tool
// answer is typed as the language adapter's data where its client file reads it: ServerHealthData.

// What the server health band keeps between draws. report is server-health.report's answer.
export type ServerHealthJson = {
  connection: 'connected' | 'reconnecting' | 'disconnected' | 'tools-missing'
  report: object | null
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
