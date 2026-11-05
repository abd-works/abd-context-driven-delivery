import type { ServerHealthData } from '@cdd/harness/health/server-health'
import type { TicketData } from '@cdd/harness/kanban/ticket'

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

// What the chat bar keeps between draws: the active session's TicketData from board.show.
export type ChatBarJson = { session: TicketData | null }

declare module 'claude-code' {
  interface PluginState {
    'cdd-board': {
      serverHealth: ServerHealthJson
      healthView: HealthViewJson
      install: InstallJson
      chatBar: ChatBarJson
      selectedFidelity: string | null
      shownStage: string | null
    }
  }
}
