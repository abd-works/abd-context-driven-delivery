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
    </span>
  )
}
