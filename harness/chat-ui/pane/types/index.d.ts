// `claude plugin validate` holds this contract to one self-contained file, so it imports nothing. Each atom's tool
// answer is typed as the language adapter's data where its client file reads it: ServerHealthData and BoardData.

// What the server health band keeps between draws. report is server-health.report's answer.
export type ServerHealthJson = {
  connection: 'connected' | 'reconnecting' | 'disconnected' | 'tools-missing'
  report: object | null
  toolCount: number
  problem: string | null
  attempt: number
}

export type HealthViewJson = { areDetailsOpen: boolean }

export type InstallJson = { state: 'idle' | 'running' | 'installed' | 'failed'; error: string | null }

// What the chat bar keeps between draws: board.show's answer, and the server's own text when the last call failed.
export type ChatBarJson = { board: object | null; problem: string | null }

// Which of the chat bar's boxes is open above the line. switchTo names the session the activation dialog opens;
// closing holds whether the active session has a branch whose work the close dialog offers to commit and push.
export type ChatBarViewJson = {
  isSessionListOpen: boolean
  isCardOpen: boolean
  switchTo: string | null
  closing: { hasBranch: boolean } | null
}

// Whether the action picker's menu is open.
export type ActionPickerJson = { isOpen: boolean }

// The files view of the selected fidelity: one tab per file ticket.files declares, its text once ticket.read_file read it.
export type FidelityFilesJson = { fidelity: string; tabs: { path: string; text: string | null }[]; shown: string | null } | null

declare module 'claude-code' {
  interface PluginState {
    'cdd-board': {
      serverHealth: ServerHealthJson
      healthView: HealthViewJson
      install: InstallJson
      chatBar: ChatBarJson
      chatBarView: ChatBarViewJson
      selectedFidelity: string | null
      actionPicker: ActionPickerJson
      fidelityFiles: FidelityFilesJson
      shownStage: string | null
    }
  }
}
