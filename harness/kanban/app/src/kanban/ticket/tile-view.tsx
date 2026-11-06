import { useBoard } from '../board/board-context'
import type { ColumnClient } from '../board/column-client'
import { CheckIcon } from '../board/icons'
import { ActionBarView } from './action-bar-view'
import type { TicketClient } from './ticket-client'
import { cellPlace } from './tile-client'

const REVIEWED_EDGE_PIXELS = 7
const EDGE_PIXELS = 3

// opensOnHover: a hover opens the bar for a look on an opened card. The details grid opens one only on a press, so
// moving the pointer across the grid does not open bar after bar.
type TileProps = { ticket: TicketClient; stage: ColumnClient; slug: string; hasPracticeChip: boolean; opensOnHover: boolean }

function TileNameView({ ticket, stage, slug }: TileProps) {
  const { page } = useBoard()
  const place = cellPlace(stage.name, slug)
  const isOn = ticket.isOn(slug)
  const practice = page.board.practiceOf(slug)
  const toggle = () => page.tiles.toggle(ticket, { ticket, stage, place, slugs: [slug] })
  return (
    <button className="tile-name" title={practice?.skillOf(slug)} disabled={!isOn} aria-expanded={page.tiles.isOpen(ticket.name, place)} onClick={() => void toggle()}>
      {practice?.fidelityNameOf(slug) ?? slug}
    </button>
  )
}

function TileHelpView({ slug }: { slug: string }) {
  const { page } = useBoard()
  const name = page.board.practiceOf(slug)?.fidelityNameOf(slug) ?? slug
  return (
    <button className="help-link" title={`Help for ${name}`} aria-label={`Help for ${name}`} onClick={() => void page.panels.openHelp(slug)}>
      ?
    </button>
  )
}

function TileHeadingView(props: TileProps) {
  const { ticket, slug, hasPracticeChip } = props
  const { page } = useBoard()
  const practice = page.board.practiceOf(slug)
  const { key, label } = ticket.stateOf(slug)
  return (
    <div className="tile-heading">
      {hasPracticeChip ? <span className="practice-chip" style={{ borderLeftColor: practice?.color }}>{practice?.name}</span> : null}
      <TileNameView {...props} />
      <span className="visually-hidden">{label}</span>
      {key === 'done' ? <CheckIcon /> : null}
      {key === 'violations' ? (
        <button className="violations-link" onClick={() => void page.panels.openReport(ticket, slug)}>
          violations
        </button>
      ) : null}
      <TileHelpView slug={slug} />
    </div>
  )
}

export function TileView(props: TileProps) {
  const { ticket, stage, slug, opensOnHover } = props
  const { page } = useBoard()
  const practice = page.board.practiceOf(slug)
  const isOn = ticket.isOn(slug)
  const place = cellPlace(stage.name, slug)
  const { key } = ticket.stateOf(slug)
  const borderColor = key === 'violations' ? 'var(--violations)' : ticket.isNext(stage, slug) ? 'var(--accent)' : 'var(--border)'
  const hover = isOn && opensOnHover ? { onMouseEnter: () => page.tiles.hoverIn({ ticket, stage, place, slugs: [slug] }), onMouseLeave: () => page.tiles.hoverOut(ticket.name, place) } : {}
  const open = isOn ? page.tiles.openOn(ticket.name, place) : undefined
  return (
    <div className="skill-cell" data-tile={slug} {...hover} style={{ opacity: ticket.lightOf(slug), borderColor, borderLeftColor: practice?.color, borderLeftWidth: key === 'done' ? REVIEWED_EDGE_PIXELS : EDGE_PIXELS }}>
      <TileHeadingView {...props} />
      {open ? <ActionBarView ticket={ticket} stage={stage} tile={open} /> : null}
    </div>
  )
}
