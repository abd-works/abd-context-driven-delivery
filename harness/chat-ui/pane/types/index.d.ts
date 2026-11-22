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

// One run of a test tier the cdd server runs on a cadence, as server-health.report lists it under test_runs.
export type TestRunJson = { name: string; state: 'running' | 'passed' | 'failed' | 'abandoned'; run_id: string; started: string; summary: string; is_new_failure: boolean }

// The runs whose new failure the chat has raised a toast for, so each is raised once; and the steps a scheduled e2e
// run's screen review judged missed by the tests, named `<review_id> <step>`, toasted once each the same way.
export type ToastedRunsJson = { runIds: string[]; missedSteps?: string[] }

// The latest scheduled e2e run's screen review, as server-health.report gives it under e2e_review.
export type E2eReviewJson = { run: string; sub_epics: number; steps: number; changed_steps: string[]; unjudged_steps: string[]; missed_steps: string[]; report: string; review_id: string }

export type InstallJson = { state: 'idle' | 'running' | 'installed' | 'failed'; error: string | null }

// The CDD version badge. data is cdd-version.check's answer, read as the chat opens; isAsking while the update dialog
// is open; problem is why it is not read yet, such as cdd still connecting; update and error say how the last Update
// and reinstall went.
export type CddVersionJson = { data: object | null; problem: string | null; isAsking: boolean; update: InstallJson['state']; error: string | null }

// The chat bar's two pushes. isAsking while Push & merge's dialog is open; state and error say how the last push went.
export type ToMainJson = { isAsking: boolean; state: InstallJson['state']; error: string | null }

// The app a person last pressed in the status row: opening while App.open readies it, failed with what failed and how to
// fix it, idle once it opened in the side panel.
// url: where the app answers once it is ready, drawn as a link; null until then.
export type AppOpeningJson = { label: string; state: 'idle' | 'opening' | 'failed'; error: string | null; url?: string | null }

// What the chat bar keeps between draws: board.overview's answer, and the server's own text when the last call failed.
// problem is why the last board read failed, cleared by the next read that works.
export type ChatBarJson = { board: object | null; problem: string | null }

// The failure shown above the chat bar's line, tools/error_display's FailureData (what failed and the context it failed
// in), typed where error-display/failure-client.ts reads it; null while none is shown. It stays until the person fixes
// or dismisses it, so a refresh never hides it.
export type FailureJson = object | null

// The prompt queue's latest failure, as the prompt-queue plugin keeps it: the queue is a plugin of its own and only its
// owner writes a value, so the board reads it and shows it on this one failure line. id grows with each failure, so a
// newer failure shows again after an older one was fixed or dismissed.
export type QueueFailureJson = { id: number; failure: string; context: string } | null

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
  // Whether the repo list, opened from its own button beside the session list's +, is open.
  isRepoListOpen: boolean
  // The repositories beside this one, as repos.siblings answers them when the repo list opens.
  repos: RepoRowJson[]
  // The folder of the repository a new session will work on, chosen with the folder picker beside the new session's
  // name; empty for the whole repository.
  newSessionFolder: string
}

// One repository in the repos folder, as repos.siblings answers it.
export type RepoRowJson = { name: string; path: string; branch: string; is_published: boolean; has_cdd: boolean }

// Whether the action picker's menu is open.
// chosenAction: the action picked from the menu, which the action button shows and runs in place of the next one.
// One format chip as ticket.format_choices answers it, and the chips held for the fidelities they were read for.
export type FormatChoiceJson = { label: string; formats: string[]; offered: number; made: number; is_chosen: boolean }
export type ActionPickerJson = { isOpen: boolean; chosenAction: string | null }
// The pattern overlays ticket.overlay_choices answers for the session the bar shows, and whether the + list box is open.
export type OverlayChoiceJson = { pattern: string; icon: string; is_chosen: boolean }
export type OverlayChoicesJson = { ticket: string; choices: OverlayChoiceJson[]; isOpen: boolean }

// The help pane's fidelity and its help as one markdown page, as fidelity-progress.help answers it; null when closed.
export type FidelityHelpJson = { fidelity: string; markdown: string } | null

// What the chat bar is doing while a ticket opens or closes, which the band shows with a turning wheel; empty when idle.
export type BusyJson = { doing: string; frame: number }

// The chat's own turns, which tell the board when a message it sent is done: whether a turn runs, how many have
// started, the check-in clock's ticks since the chat last worked, and each message still worked on with the turns
// started before it arrived.
export type ChatTurnsJson = { isBusy: boolean; turnsStarted: number; idleCheckIns: number; unfinished: Record<string, number> }

declare module 'claude-code' {
  interface PluginState {
    'cdd-board': {
      serverHealth: ServerHealthJson
      healthView: HealthViewJson
      toastedRuns: ToastedRunsJson
      install: InstallJson
      cddVersion: CddVersionJson
      toMain: ToMainJson
      appOpening: AppOpeningJson
      chatBar: ChatBarJson
      failure: FailureJson
      // The id of the prompt queue's failure that Fix or ✕ last handled, which the line no longer shows.
      handledQueueFailure: number
      chatBarView: ChatBarViewJson
      actionPicker: ActionPickerJson
      fidelityHelp: FidelityHelpJson
      guidance: object | null
      overlayChoices: OverlayChoicesJson
      busy: BusyJson
      chatTurns: ChatTurnsJson
      // The name a person reads for this chat in the board's chat picker.
      chatName: string
      // The check-ins with cdd failed in a row, which the bar shows once they reach ten.
      failedCheckIns: number
    }
    'prompt-queue': {
      failure: QueueFailureJson
    }
  }
}
