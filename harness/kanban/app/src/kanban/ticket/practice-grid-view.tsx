import { PRACTICES } from '../board/board-brand'
import type { Practice } from '../board/board-brand'
import { useBoard } from '../board/board-context'
import type { ColumnClient } from '../board/column-client'
import { ChevronIcon } from '../board/icons'
import { StageHeadView } from '../board/stage-head-view'
import { ActionBarView } from './action-bar-view'
import type { TicketClient } from './ticket-client'
import { headPlace } from './tile-client'
import { TileView } from './tile-view'

function GridCornerView() {
  const { page, state } = useBoard()
  const label = state.hidesDisabled ? 'Show practices not enabled' : 'Hide practices not enabled'
  return (
    <div className="grid-corner">
      <span>context-driven-delivery</span>
      <button className="icon-button corner-toggle" aria-label={label} aria-expanded={!state.hidesDisabled} title={label} onClick={() => page.layout.toggleHiddenPractices()}>
        <ChevronIcon isTurned={state.hidesDisabled} />
      </button>
    </div>
  )
}

function GridStageHeadView({ ticket, stage }: { ticket: TicketClient; stage: ColumnClient }) {
  const { page } = useBoard()
  const place = headPlace(stage.name)
  const spot = { ticket: ticket.name, stage, place, slugs: ticket.enabledSlugs(stage) }
  const isOpen = page.tiles.isOpen(ticket.name, place)
  return (
    <StageHeadView stage={stage.name} onMouseEnter={() => page.tiles.hoverIn(spot)} onMouseLeave={() => page.tiles.hoverOut(place)}>
      <button className="expand-mark" aria-label={`Actions for ${stage.name}`} aria-expanded={isOpen} onClick={() => void page.tiles.toggle(ticket, spot)}>
        {isOpen ? '▴' : '▾'}
      </button>
    </StageHeadView>
  )
}

// A stage head's bar sits under the heads in the stage's own column, so it holds every practice of that stage.
function StageBarView({ ticket }: { ticket: TicketClient }) {
  const { page, state } = useBoard()
  const { tile } = state
  const stages = page.board.stages
  // Each read of stages builds new clients, so the bar finds its stage by position in one list.
  const index = stages.findIndex(entry => tile?.ticket === ticket.name && tile.place === headPlace(entry.name))
  const stage = stages[index]
  if (!tile || !stage) return null
  const place = headPlace(stage.name)
  return (
    <div className="column-grid details-grid">
      <div style={{ gridColumn: index + 2 }}>
        <ActionBarView ticket={ticket} stage={stage} tile={tile} onMouseEnter={() => page.tiles.hoverIn({ ticket: ticket.name, stage, place, slugs: tile.slugs })} onMouseLeave={() => page.tiles.hoverOut(place)} />
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
        const slug = stage.workRequired.find(required => required.startsWith(practice.prefix))
        return slug ? <TileView key={slug} ticket={ticket} stage={stage} slug={slug} hasPracticeChip={false} /> : <span key={stage.name} />
      })}
      <span />
    </div>
  )
}

export function PracticeGridView({ ticket }: { ticket: TicketClient }) {
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
