import type { MouseEvent } from 'react'

import { useBoard } from '../shared/board-context'
import { FileViewIcon } from '../shared/icons'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { TicketClient } from './ticket-client'

// Opens the files panel on the fidelities given: the whole card's on a card, one fidelity's in its action bar.
export function FileViewsView({ ticket, progress }: { ticket: TicketClient; progress: FidelityProgressClient[] }) {
  const { page } = useBoard()
  // A press on a card would also select it; opening its files is enough.
  const opened = (event: MouseEvent) => {
    if (event.currentTarget.closest('.ticket-card')) event.stopPropagation()
    void page.files.openFiles(ticket, progress)
  }
  return (
    <span className="file-views">
      <button className="file-view" aria-label="files" title="View the files" onClick={opened}>
        <FileViewIcon mode="files" />
      </button>
    </span>
  )
}
