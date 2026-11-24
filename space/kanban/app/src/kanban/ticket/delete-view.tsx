import type { KeyboardEvent } from 'react'

import { useBoard } from '../shared/board-context'

// The Delete dialog, which asks before a ticket and its whole session folder go, since that cannot be undone. It is the
// board's own dialog, not the browser's confirm, which Claude's Browser pane answers No without showing.
export function DeleteDialogView() {
  const { page, state } = useBoard()
  const ticket = state.deleting
  if (!ticket) return null
  const cancel = () => page.store.change({ deleting: null })
  const remove = () => {
    page.store.change({ deleting: null })
    void ticket.delete()
  }
  const pressed = (event: KeyboardEvent) => {
    if (event.key === 'Escape') cancel()
  }
  return (
    <div className="dialog-backdrop" onKeyDown={pressed}>
      <div role="dialog" aria-modal="true" aria-labelledby="delete-title" className="dialog">
        <h2 id="delete-title">Delete {ticket.title}</h2>
        <p>Delete {ticket.title} and its session folder? This cannot be undone.</p>
        <div className="dialog-actions">
          <button className="action" type="button" autoFocus onClick={cancel}>
            Cancel
          </button>
          <button className="action primary" type="button" onClick={remove}>
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}
