import type { MouseEvent } from 'react'

import { useBoard } from '../shared/board-context'
import { FileViewIcon } from '../shared/icons'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { TicketClient } from './ticket-client'

const FILE_VIEWS = [
  { mode: 'folder', hint: 'Browse the folder' },
  { mode: 'files', hint: 'View the files' },
]

// Opens the files panel on the fidelities given: the whole card's on a card, one fidelity's in its action bar.
export function FileViewsView({ ticket, progress }: { ticket: TicketClient; progress: FidelityProgressClient[] }) {
  const { page } = useBoard()
  // A press on a card would also select it; opening its files is enough.
  const opened = (mode: string) => (event: MouseEvent) => {
    if (event.currentTarget.closest('.ticket-card')) event.stopPropagation()
    void page.files.openFiles(ticket, progress, mode)
  }
  return (
    <span className="file-views">
      {FILE_VIEWS.map(({ mode, hint }) => (
        <button key={mode} className="file-view" aria-label={mode} title={hint} onClick={opened(mode)}>
          <FileViewIcon mode={mode} />
        </button>
      ))}
      <GraphWidgetView ticket={ticket} />
    </span>
  )
}

// Opens the Graph app on the ticket's worktree, where its session is the open one, so the graph shows the ticket's
// practice roots and only the practices it works on. A ticket not yet activated has no worktree to open it on.
function GraphWidgetView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const hint = ticket.worktree ? "Open the knowledge graph on this ticket's practice roots" : 'Activate this ticket to open its knowledge graph'
  const opened = (event: MouseEvent) => {
    if (event.currentTarget.closest('.ticket-card')) event.stopPropagation()
    void page.editorApp.openOn(page.editorApp.graph, ticket.worktree)
  }
  return (
    <button className="file-view" aria-label="graph" title={hint} disabled={!ticket.worktree} onClick={opened}>
      <FileViewIcon mode="graph" />
    </button>
  )
}
