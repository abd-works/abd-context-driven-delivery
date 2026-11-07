import { ItemBarView } from '../backlog-item/backlog-item-view'
import { useBoard } from '../board/board-context'
import { ExpandIcon } from '../board/icons'
import { PracticeGridView } from './practice-grid-view'
import type { TicketClient } from './ticket-client'
import { slugsOf } from './tile-client'

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

function PlaceLinkView({ label, hint, isOff = false, onPress }: { label: string; hint: string; isOff?: boolean; onPress: () => unknown }) {
  return (
    <button className="place-link" title={hint} disabled={isOff} onClick={() => void onPress()}>
      {label}
    </button>
  )
}

// The ticket's place and notes, each a way in: its session folder, its stage's files, its latest handoff, its next step.
function TicketBarView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const stage = page.board.stageOf(ticket)
  const stageSlugs = stage ? slugsOf(ticket.enabledFidelities(stage)) : []
  return (
    <div className="details-bar-words">
      <div className="details-heading">
        <div className="details-title">
          <h2>{ticket.title}</h2>
          <span className="details-place">
            <PlaceLinkView label={ticket.name} hint="Browse the session folder" onPress={() => page.files.openSessionFolder(ticket)} />
            {ticket.origin ? ` · ${ticket.origin}` : ''}
            {' · root '}
            <PlaceLinkView label={ticket.session.workpath || 'whole repository'} hint="Choose the session's workpath and each practice's practice root" onPress={() => page.roots.openFor(ticket)} />
            {' · '}
            <PlaceLinkView label={ticket.stagePlace} hint={`Browse the files of ${stage?.name ?? 'this stage'}`} isOff={!stageSlugs.length} onPress={() => page.files.openFiles(ticket, stageSlugs, 'folder')} />
          </span>
        </div>
        <div className="details-place">
          {ticket.session.handoff ? (
            <>
              Latest handoff: <PlaceLinkView label={ticket.session.handoff} hint="Open the handoff" onPress={() => page.files.openSessionFile(ticket, ticket.session.handoff)} />
            </>
          ) : (
            'No handoff yet'
          )}
          {ticket.nextNote ? (
            <>
              {' · '}
              <PlaceLinkView label={ticket.nextNote} hint={ticket.runNextHint} isOff={!ticket.canRunNext} onPress={() => ticket.runNext()} />
            </>
          ) : null}
          {ticket.lockNote ? ` · ${ticket.lockNote}` : ''}
        </div>
      </div>
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
