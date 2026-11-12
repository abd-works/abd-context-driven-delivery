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
// problem is why the last board read failed, cleared by the next read that works. failure is an action the person ran
// that failed, such as opening a ticket or a close, kept until they dismiss it, so a refresh never hides it.
export type ChatBarJson = { board: object | null; problem: string | null; failure: string | null }

// Which of the chat bar's boxes is open above the line. closing holds the branch the active session's work is on,
// checked out, whose work the close dialog offers to commit and push, or null. leaveChoices is what the Python Ticket
// offers the close dialog, in its order; leaving is what the dialog has chosen of them, as ticket.close takes them.
export type ChatBarViewJson = {
  isSessionListOpen: boolean
  isCardOpen: boolean
  closing: { branch: string | null } | null
  leaveChoices: string[]
  // The branch leaving commits and pushes, which the LEAVE line names; empty when nothing checked out is the session's.
  leaveBranch: string
  // The session's own branch, which merge and delete branch act on, checked out or not; empty while git has none.
  leaveOwnBranch: string
  leaving: string[]
}

// Whether the action picker's menu is open.
// chosenAction: the action picked from the menu, which the action button shows and runs in place of the next one.
// One format chip as ticket.format_choices answers it, and the chips held for the fidelities they were read for.
export type FormatChoiceJson = { label: string; formats: string[]; offered: number; made: number; starts_picked: boolean }
export type FormatChoicesJson = { key: string; choices: FormatChoiceJson[]; picked: string[] | null }
export type ActionPickerJson = { isOpen: boolean; chosenAction: string | null }
// The pattern overlays ticket.overlay_choices answers for the session the bar shows, and whether the + list box is open.
export type OverlayChoiceJson = { pattern: string; icon: string; is_chosen: boolean }
export type OverlayChoicesJson = { ticket: string; choices: OverlayChoiceJson[]; isOpen: boolean }

// The files view of the selected fidelity: one tab per file fidelity-progress.files declares, its text once session.read_file read it.
// isOutOfDate: a report's saved graph is in a shape the graph no longer reads, so the tab offers Validate again.
export type FidelityFilesJson = { fidelity: string; tabs: { path: string; text: string | null; exists: boolean }[]; shown: string | null; isOutOfDate: boolean } | null

// What the chat bar is doing while a ticket opens or closes, which the band shows with a turning wheel; empty when idle.
export type BusyJson = { doing: string; frame: number }

declare module 'claude-code' {
  interface PluginState {
    'cdd-board': {
      serverHealth: ServerHealthJson
      healthView: HealthViewJson
      install: InstallJson
      chatBar: ChatBarJson
      chatBarView: ChatBarViewJson
      selectedFidelities: string[]
      actionPicker: ActionPickerJson
      fidelityFiles: FidelityFilesJson
      shownStage: string | null
      stagePicker: boolean
      formatChoices: FormatChoicesJson
      overlayChoices: OverlayChoicesJson
      busy: BusyJson
    }
  }
}
