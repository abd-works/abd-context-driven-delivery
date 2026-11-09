// `claude plugin validate` holds this contract to one self-contained file, so it imports nothing. Each atom's tool
// answer is typed as the language adapter's data where its client file reads it: ServerHealthData and BoardOverviewData.

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

// What the chat bar keeps between draws: board.overview's answer, and the server's own text when the last call failed.
export type ChatBarJson = { board: object | null; problem: string | null }

// Which of the chat bar's boxes is open above the line. switchTo names the session the activation dialog opens;
// closing holds the branch the active session's work is on, checked out, whose work the close dialog offers to commit
// and push, or null. leaveChoices and openChoices are what the Python Ticket offers the open dialog, in its order;
// leaving and opening are what the dialog has chosen of them, as ticket.activate and ticket.close take them.
export type ChatBarViewJson = {
  isSessionListOpen: boolean
  isCardOpen: boolean
  switchTo: string | null
  closing: { branch: string | null } | null
  leaveChoices: string[]
  // The branch leaving acts on, which the LEAVE line names; empty when nothing checked out is the session's.
  leaveBranch: string
  leaving: string[]
  openChoices: string[]
  // The branches that could each be the session's when more than one holds its name; none is chosen for it.
  candidateBranches: string[]
  opening: string[]
}

// Whether the action picker's menu is open.
// chosenAction: the action picked from the menu, which the action button shows and runs in place of the next one.
export type ActionPickerJson = { isOpen: boolean; chosenAction: string | null }

// The files view of the selected fidelity: one tab per file fidelity-progress.files declares, its text once session.read_file read it.
// isOutOfDate: a report's saved graph is in a shape the graph no longer reads, so the tab offers Validate again.
export type FidelityFilesJson = { fidelity: string; tabs: { path: string; text: string | null }[]; shown: string | null; isOutOfDate: boolean } | null

// Where this chat works (its session root) and where the active session's work is (its ticket's worktree, else the
// main checkout), so the band can say when they differ.
export type ChatFolderJson = { current: string; expected: string }

// What the chat bar is doing while a switch or close runs, which the band shows with a turning wheel; empty when idle.
export type BusyJson = { doing: string; frame: number }

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
      chatFolder: ChatFolderJson
      busy: BusyJson
    }
  }
}
