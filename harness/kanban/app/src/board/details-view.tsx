import type { Column } from './board'
import { PRACTICES } from './board-brand'
import type { Practice } from './board-brand'
import { useBoard } from './board-context'
import { ActionBarView } from './action-bar-view'
import { ChevronIcon, ExpandIcon } from './icons'
import { StageHeadView } from './stage-head-view'
import type { TicketClient } from './ticket-client'
import { headPlace } from './tile-client'
import { TileView } from './tile-view'

function ExpandDetailsView() {
  const { page, state } = useBoard()
  const isExpanded = state.expandedRegion === 'details'
  const label = isExpanded ? 'Collapse details' : 'Expand details'
  return (
    <button className="icon-button" aria-label={label} title={label} onClick={() => page.board.toggleRegion('details')}>
      <ExpandIcon isExpanded={isExpanded} />
    </button>
  )
}

function TicketActionsView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const isOff = ticket.isClosed || ticket.isLocked
  const cannotSend = !page.chat.canSend
  return (
    <div className="details-actions">
      <button className="action" disabled={!ticket.canRunNext} onClick={() => void ticket.runNext()}>
        {ticket.runNextLabel}
      </button>
      <button className="action" disabled={isOff || cannotSend} onClick={() => void ticket.fillSplit()}>
        Split
      </button>
      <button className="action" disabled={ticket.isActive || ticket.isClosed} onClick={() => void page.activation.start(ticket, false)}>
        Switch to
      </button>
      <button className="action" disabled={isOff || cannotSend} onClick={() => void ticket.fillHandoff()}>
        Handoff
      </button>
      <button className="action" disabled={!ticket.isActive || ticket.isClosed} onClick={() => void page.activation.start(ticket, true)}>
        Close session
      </button>
      <button className="action" disabled={ticket.isLocked && !ticket.isClosed} onClick={() => void ticket.archive()}>
        Archive
      </button>
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

function ItemBarView() {
  const { page } = useBoard()
  const json = page.board.selectedItem
  if (!json) return null
  const item = page.item(json)
  return (
    <div className="details-bar-words">
      <div className="details-heading">
        <div className="details-title">
          <h2>{item.title}</h2>
          <span className="details-place">{item.path}</span>
        </div>
        {item.text ? <p className="item-text">{item.text}</p> : null}
      </div>
      <button className="action primary" onClick={() => void item.start()}>
        Start
      </button>
    </div>
  )
}

function GridCornerView() {
  const { page, state } = useBoard()
  const label = state.hidesDisabled ? 'Show practices not enabled' : 'Hide practices not enabled'
  return (
    <div className="grid-corner">
      <span>context-driven-delivery</span>
      <button className="icon-button corner-toggle" aria-label={label} aria-expanded={!state.hidesDisabled} title={label} onClick={() => page.board.toggleHiddenPractices()}>
        <ChevronIcon isTurned={state.hidesDisabled} />
      </button>
    </div>
  )
}

function GridStageHeadView({ ticket, stage }: { ticket: TicketClient; stage: Column }) {
  const { page } = useBoard()
  const place = headPlace(stage.name)
  const slugs = ticket.enabledSlugs(stage)
  const isOpen = page.tiles.isOpen(ticket.name, place)
  return (
    <StageHeadView stage={stage.name} onMouseEnter={() => page.tiles.hoverIn(ticket.name, stage, place, slugs)} onMouseLeave={() => page.tiles.hoverOut(place)}>
      <button className="expand-mark" aria-label={`Actions for ${stage.name}`} aria-expanded={isOpen} onClick={() => void page.tiles.toggle(ticket, stage, place, slugs)}>
        {isOpen ? '▴' : '▾'}
      </button>
    </StageHeadView>
  )
}

// A stage head's bar sits under the heads in the stage's own column, so it holds every practice of that stage.
function StageBarView({ ticket }: { ticket: TicketClient }) {
  const { page, state } = useBoard()
  const { tile } = state
  const stage = page.board.stages.find(entry => tile?.ticket === ticket.name && tile.place === headPlace(entry.name))
  if (!tile || !stage) return null
  const place = headPlace(stage.name)
  return (
    <div className="column-grid details-grid">
      <div style={{ gridColumn: page.board.stages.indexOf(stage) + 2 }}>
        <ActionBarView ticket={ticket} stage={stage} tile={tile} hasFileLinks onMouseEnter={() => page.tiles.hoverIn(ticket.name, stage, place, tile.slugs)} onMouseLeave={() => page.tiles.hoverOut(place)} />
      </div>
    </div>
  )
}

function PracticeLabelView({ ticket, practice }: { ticket: TicketClient; practice: Practice }) {
  const { page } = useBoard()
  const isOn = ticket.isEnabled(practice.key)
  const label = `${isOn ? 'Disable' : 'Enable'} ${practice.name} for ${ticket.title}`
  return (
    <div className="practice-label" style={{ borderLeftColor: practice.color }}>
      <button className="readme-link" style={{ opacity: isOn ? 1 : 0.5 }} onClick={() => void page.panels.openHelp(practice.key, '')}>
        {practice.name}
      </button>
      <input type="checkbox" role="switch" className="practice-switch" title={label} aria-label={label} checked={isOn} disabled={ticket.isLocked} onChange={() => void ticket.enablePractice(practice.key, !isOn)} />
    </div>
  )
}

function PracticeLineView({ ticket, practice }: { ticket: TicketClient; practice: Practice }) {
  const { page } = useBoard()
  return (
    <div className="column-grid details-grid">
      <PracticeLabelView ticket={ticket} practice={practice} />
      {page.board.stages.map(stage => {
        const slug = (stage.work_required ?? []).find(required => required.startsWith(practice.prefix))
        return slug ? <TileView key={slug} ticket={ticket} stage={stage} slug={slug} hasPracticeChip={false} /> : <span key={stage.name} />
      })}
      <span />
    </div>
  )
}

function PracticeGridView({ ticket }: { ticket: TicketClient }) {
  const { page, state } = useBoard()
  const shown = PRACTICES.filter(practice => ticket.isEnabled(practice.key) || !state.hidesDisabled)
  return (
    <div className="details-lines">
      <div className="column-grid details-grid">
        <GridCornerView />
        {page.board.stages.map(stage => (
          <GridStageHeadView key={stage.name} ticket={ticket} stage={stage} />
        ))}
        <span />
      </div>
      <StageBarView ticket={ticket} />
      {shown.map(practice => (
        <PracticeLineView key={practice.key} ticket={ticket} practice={practice} />
      ))}
    </div>
  )
}

export function DetailsView() {
  const { page } = useBoard()
  const json = page.board.selectedTicket
  const ticket = json ? page.ticket(json) : null
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
