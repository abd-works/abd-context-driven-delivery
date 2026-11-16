import { ItemBarView } from '../backlog-item/backlog-item-view'
import { useBoard } from '../shared/board-context'
import { ExpandIcon } from '../shared/icons'
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
  return (
    <div className="details-bar-words">
      <div className="details-heading">
        <div className="details-title">
          <h2>{ticket.title}</h2>
          <TicketPlaceView ticket={ticket} />
        </div>
        <TicketNotesView ticket={ticket} />
      </div>
    </div>
  )
}

// Where the ticket works: its session folder, the folder its session works in, its roots, and its stage's files.
function TicketPlaceView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const stage = page.board.stageOf(ticket)
  const stageProgress = stage ? ticket.work.progressIn(stage) : []
  return (
    <span className="details-place">
      <PlaceLinkView label={ticket.name} hint="Browse the session folder" onPress={() => page.files.openFolder(ticket, 'session')} />
      {ticket.face.origin ? ` · ${ticket.face.origin}` : ''}
      {' · root '}
      <PlaceLinkView label={ticket.session.workpath || 'whole repository'} hint="Browse the folder the session works in" onPress={() => page.files.openFolder(ticket, 'workpath')} />{' '}
      <PlaceLinkView label="roots" hint="Choose the session's workpath and each practice's practice root" onPress={() => page.roots.openFor(ticket)} />
      {' · '}
      <PlaceLinkView label={ticket.face.stagePlace} hint={`Browse the files of ${stage?.name ?? 'this stage'}`} isOff={!stageProgress.length} onPress={() => page.files.openFiles(ticket, stageProgress)} />
    </span>
  )
}

// The ticket's notes: its latest handoff, its next step, and what locks it.
function TicketNotesView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  return (
    <div className="details-place">
      {ticket.session.handoff ? (
        <>
          Latest handoff: <PlaceLinkView label={ticket.session.handoff} hint="Open the handoff" onPress={() => page.files.openFolder(ticket, 'session', ticket.session.handoff)} />
        </>
      ) : (
        'No handoff yet'
      )}
      {ticket.face.nextNote ? (
        <>
          {' · '}
          <PlaceLinkView label={ticket.face.nextNote} hint={ticket.face.runNextHint} isOff={!ticket.nextStep.canRun} onPress={() => ticket.nextStep.run()} />
        </>
      ) : null}
      {ticket.face.lockNote ? ` · ${ticket.face.lockNote}` : ''}
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
