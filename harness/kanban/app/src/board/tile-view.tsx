import type { ActionStates, Column } from './board'
import { guidanceSlug } from './board'
import { ACTION_STANDINGS, fidelityOf, practiceOf } from './board-brand'
import { useBoard } from './board-context'
import { ActionBarView } from './action-bar-view'
import { CheckIcon } from './icons'
import type { TicketClient } from './ticket-client'
import { skillOf } from './ticket-client'
import { cellPlace } from './tile-client'

const ACTION_ORDER: (keyof ActionStates)[] = ['generate', 'validate', 'review']
const OFF_LIGHT = 0.2
const NOT_STARTED_LIGHT = 0.45

// Generate, Validate, and Review on one fidelity, each to do, in progress, or done.
function ActionMarksView({ ticket, slug }: { ticket: TicketClient; slug: string }) {
  const actions = ticket.actionsOf(slug)
  return (
    <span className="action-marks">
      {ACTION_ORDER.map(action => {
        const standing = ACTION_STANDINGS[actions[action]] ?? ACTION_STANDINGS.to_do!
        return (
          <span key={action} role="img" title={`${action}: ${standing.label}`} aria-label={`${action}: ${standing.label}`} style={{ color: standing.color }}>
            {standing.mark}
          </span>
        )
      })}
    </span>
  )
}

function tileLightOf(ticket: TicketClient, stage: Column, slug: string, isOn: boolean): number {
  if (!isOn) return OFF_LIGHT
  return ticket.stateOf(slug).key === 'not_started' && !ticket.isNext(stage, slug) ? NOT_STARTED_LIGHT : 1
}

type TileProps = { ticket: TicketClient; stage: Column; slug: string; hasPracticeChip: boolean }

function TileHeadingView({ ticket, stage, slug, hasPracticeChip }: TileProps) {
  const { page } = useBoard()
  const practice = practiceOf(slug)
  const fidelity = fidelityOf(slug)
  const name = guidanceSlug(fidelity)
  const { key, label } = ticket.stateOf(slug)
  const isOn = ticket.isEnabled(practice?.key ?? '')
  const toggle = () => page.tiles.toggle(ticket, stage, cellPlace(stage.name, slug), [slug])
  return (
    <div className="tile-heading">
      {hasPracticeChip ? <span className="practice-chip" style={{ borderLeftColor: practice?.color }}>{practice?.name}</span> : null}
      <button className="tile-name" title={skillOf(slug)} disabled={!isOn} aria-expanded={page.tiles.isOpen(ticket.name, cellPlace(stage.name, slug))} onClick={() => void toggle()}>
        {name}
      </button>
      <span className="visually-hidden">{label}</span>
      <ActionMarksView ticket={ticket} slug={slug} />
      {key === 'done' ? <CheckIcon /> : null}
      {key === 'violations' ? (
        <button className="violations-link" onClick={() => void page.panels.openReport(ticket.name, slug)}>
          violations
        </button>
      ) : null}
      <button className="help-link" title={`Help for ${name}`} aria-label={`Help for ${name}`} onClick={() => void page.panels.openHelp(practice?.key ?? '', fidelity)}>
        ?
      </button>
    </div>
  )
}

export function TileView(props: TileProps) {
  const { ticket, stage, slug } = props
  const { page, state } = useBoard()
  const practice = practiceOf(slug)
  const isOn = ticket.isEnabled(practice?.key ?? '')
  const place = cellPlace(stage.name, slug)
  const { key } = ticket.stateOf(slug)
  const borderColor = key === 'violations' ? 'var(--violations)' : ticket.isNext(stage, slug) ? 'var(--accent)' : 'var(--border)'
  const hover = isOn ? { onMouseEnter: () => page.tiles.hoverIn(ticket.name, stage, place, [slug]), onMouseLeave: () => page.tiles.hoverOut(place) } : {}
  const open = isOn && page.tiles.isOpen(ticket.name, place) ? state.tile : null
  return (
    <div className="skill-cell" data-tile={slug} {...hover} style={{ opacity: tileLightOf(ticket, stage, slug, isOn), borderColor, borderLeftColor: practice?.color, borderLeftWidth: key === 'done' ? 7 : 3 }}>
      <TileHeadingView {...props} />
      {open ? <ActionBarView ticket={ticket} stage={stage} tile={open} hasFileLinks /> : null}
    </div>
  )
}
