import { ItemBarView } from '../backlog-item/backlog-item-view'
import { useBoard } from '../board/board-context'
import { ExpandIcon } from '../board/icons'
import { PracticeGridView } from './practice-grid-view'
import type { TicketClient } from './ticket-client'

function ExpandDetailsView() {
  const { page, state } = useBoard()
  const isExpanded = state.expandedRegion === 'details'
  const label = isExpanded ? 'Collapse details' : 'Expand details'
  return (
    <button className="icon-button" aria-label={label} title={label} onClick={() => page.layout.toggleRegion('details')}>
      <ExpandIcon isExpanded={isExpanded} />
    </button>
  )
}

function DetailsActionView({ label, isOff, onPress }: { label: string; isOff: boolean; onPress: () => unknown }) {
  return (
    <button className="action" disabled={isOff} onClick={() => void onPress()}>
      {label}
    </button>
  )
}

function TicketActionsView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const cannotFill = ticket.isClosed || ticket.isLocked || !page.chat.canSend
  return (
    <div className="details-actions">
      <DetailsActionView label={ticket.runNextLabel} isOff={!ticket.canRunNext} onPress={() => ticket.runNext()} />
      <DetailsActionView label="Split" isOff={cannotFill} onPress={() => ticket.fillSplit()} />
      <DetailsActionView label="Switch to" isOff={ticket.isActive || ticket.isClosed} onPress={() => page.activation.start(ticket, false)} />
      <DetailsActionView label="Handoff" isOff={cannotFill} onPress={() => ticket.fillHandoff()} />
      <DetailsActionView label="Close session" isOff={!ticket.isActive || ticket.isClosed} onPress={() => page.activation.start(ticket, true)} />
      <DetailsActionView label="Archive" isOff={ticket.isLocked && !ticket.isClosed} onPress={() => ticket.archive()} />
    </div>
  )
}

function TicketBarView({ ticket }: { ticket: TicketClient }) {
  return (
    <div className="details-bar-words">
      <div className="details-heading">
        <div className="details-title">
          <h2>{ticket.title}</h2>
          <span className="details-place">{ticket.place}</span>
        </div>
        <div className="details-place">{ticket.footer}</div>
      </div>
      <TicketActionsView ticket={ticket} />
    </div>
  )
}

export function DetailsView() {
  const { page } = useBoard()
  const ticket = page.board.selectedTicket
  return (
    <div className="details-region">
      <div className="details-bar">
        {ticket ? <TicketBarView ticket={ticket} /> : <ItemBarView />}
        <ExpandDetailsView />
      </div>
      <section className="details-body" aria-label="Details">
        {ticket ? <PracticeGridView ticket={ticket} /> : null}
      </section>
    </div>
  )
}
