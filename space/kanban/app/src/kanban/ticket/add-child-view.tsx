import { useState } from 'react'
import type { KeyboardEvent, MouseEvent } from 'react'

import { SessionActionIcon } from '../shared/icons'
import type { TicketClient } from './ticket-client'

// A child added by hand: the plus opens a title field on the card, Enter adds the child, Escape leaves it.
export function AddChildView({ ticket }: { ticket: TicketClient }) {
  const [title, setTitle] = useState<string | null>(null)
  const kept = (event: MouseEvent) => event.stopPropagation()
  const pressed = (event: KeyboardEvent<HTMLInputElement>) => {
    event.stopPropagation()
    if (event.key === 'Escape') setTitle(null)
    if (event.key !== 'Enter' || !title?.trim()) return
    void ticket.addChild(title.trim())
    setTitle(null)
  }
  if (title === null) {
    return (
      <button className="file-view" aria-label="Add child" title="Add a child ticket" disabled={ticket.isClosed || ticket.isMain} onClick={event => (kept(event), setTitle(''))}>
        <SessionActionIcon action="child" />
      </button>
    )
  }
  return <input className="child-title" aria-label="Child title" placeholder="Child title, then Enter" value={title} autoFocus onClick={kept} onChange={event => setTitle(event.target.value)} onKeyDown={pressed} onBlur={() => setTitle(null)} />
}
