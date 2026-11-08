import { useBoard } from '../shared/board-context'
import type { ColumnClient } from '../board/column-client'
import type { PracticeClient } from '../board/practice-client'
import { ChevronIcon } from '../shared/icons'
import { StageHeadView } from '../shared/stage-head-view'
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
  const spot = { ticket, stage, place, fidelities: ticket.progressIn(stage).map(progress => progress.fidelity) }
  const isOpen = page.tiles.isOpen(ticket.name, place)
  return (
    <StageHeadView stage={stage}>
      <button className="expand-mark" aria-label={`Actions for ${stage.name}`} aria-expanded={isOpen} onClick={() => void page.tiles.toggle(ticket, spot)}>
        {isOpen ? '▴' : '▾'}
      </button>
    </StageHeadView>
  )
}

// Each open stage head's bar sits under the heads in the stage's own column, so it holds every practice of that
// stage. Bars of several stages share the one line, side by side.
function StageBarsView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  // Each read of stages builds new clients, so every bar finds its stage by position in one list.
  const stages = page.board.stages
  const open = stages.flatMap((stage, index) => {
    const tile = page.tiles.openOn(ticket.name, headPlace(stage.name))
    return tile ? [{ stage, index, tile }] : []
  })
  if (!open.length) return null
  return (
    <div className="column-grid details-grid">
      {open.map(({ stage, index, tile }) => (
        <div key={stage.name} style={{ gridColumn: index + 2, gridRow: 1 }}>
          <ActionBarView ticket={ticket} tile={tile} />
        </div>
      ))}
    </div>
  )
}

function PracticeLabelView({ ticket, practice }: { ticket: TicketClient; practice: PracticeClient }) {
  const { page } = useBoard()
  const isOn = ticket.isEnabled(practice.key)
  const label = `${isOn ? 'Disable' : 'Enable'} ${practice.name} for ${ticket.title}`
  return (
    <div className={isOn ? 'practice-label' : 'practice-label is-off'} style={{ borderLeftColor: practice.color }}>
      <button className="readme-link" onClick={() => void page.panels.openPracticeHelp(practice)}>
        {practice.name}
      </button>
      <input type="checkbox" role="switch" className="practice-switch" title={label} aria-label={label} checked={isOn} disabled={ticket.isLocked} onChange={() => void ticket.enablePractice(practice.key, !isOn)} />
    </div>
  )
}

function PracticeLineView({ ticket, practice }: { ticket: TicketClient; practice: PracticeClient }) {
  const { page } = useBoard()
  return (
    <div className="column-grid details-grid">
      <PracticeLabelView ticket={ticket} practice={practice} />
      {page.board.stages.map(stage => {
        const progress = ticket.progressOn(stage.workRequired.filter(required => practice.has(required.slug)))[0]
        return progress ? <TileView key={progress.fidelity.slug} ticket={ticket} stage={stage} progress={progress} hasPracticeChip={false} opensOnHover={false} /> : <span key={stage.name} />
      })}
      <span />
    </div>
  )
}

export function PracticeGridView({ ticket }: { ticket: TicketClient }) {
  const { page, state } = useBoard()
  const shown = page.board.shownPractices.filter(practice => ticket.isEnabled(practice.key) || !state.hidesDisabled)
  return (
    <div className="details-lines">
      <div className="column-grid details-grid">
        <GridCornerView />
        {page.board.stages.map(stage => (
          <GridStageHeadView key={stage.name} ticket={ticket} stage={stage} />
        ))}
        <span />
      </div>
      <StageBarsView ticket={ticket} />
      {shown.map(practice => (
        <PracticeLineView key={practice.key} ticket={ticket} practice={practice} />
      ))}
    </div>
  )
}
