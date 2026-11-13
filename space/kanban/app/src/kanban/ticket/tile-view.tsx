import { useBoard } from '../shared/board-context'
import type { ColumnClient } from '../board/column-client'
import { CheckIcon } from '../shared/icons'
import { ActionBarView } from './action-bar-view'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { TicketClient } from './ticket-client'
import { cellPlace } from './tile-client'

const DONE_EDGE_PIXELS = 7
const EDGE_PIXELS = 3

// opensOnHover: a hover opens the bar for a look on an opened card. The details grid opens one only on a press, so
// moving the pointer across the grid does not open bar after bar. progress is the ticket's progress on the tile's
// fidelity, whose practice its session may have turned off.
type TileProps = { ticket: TicketClient; stage: ColumnClient; progress: FidelityProgressClient; hasPracticeChip: boolean; opensOnHover: boolean }

function TileNameView({ ticket, stage, progress }: TileProps) {
  const { page } = useBoard()
  const { fidelity } = progress
  const slug = fidelity.slug
  const place = cellPlace(stage.name, fidelity)
  const shown = page.board.fidelityShown(slug)
  const toggle = () => page.tiles.toggle(ticket, { ticket, stage, place, fidelities: [fidelity] })
  return (
    <button className="tile-name" title={shown?.skill} disabled={!progress.isEnabled} aria-expanded={page.tiles.isOpen(ticket.name, place)} onClick={() => void toggle()}>
      {shown?.label ?? slug}
    </button>
  )
}

function TileHelpView({ progress }: { progress: FidelityProgressClient }) {
  const { page } = useBoard()
  const name = page.board.fidelityShown(progress.fidelity.slug)?.label ?? progress.fidelity.slug
  return (
    <button className="help-link" title={`Help for ${name}`} aria-label={`Help for ${name}`} onClick={() => void page.panels.openFidelityHelp(progress)}>
      ?
    </button>
  )
}

// The small widget on a row whose practice an app edits, which Python puts on the practice's first fidelity only
// (BoardFidelity.editor): the Story UI editor on the Stories story-map row. It opens the editor on the ticket's
// worktree, where the ticket's session is the open one; a ticket not yet activated has no worktree to open it on.
function EditorWidgetView({ ticket, progress }: { ticket: TicketClient; progress: FidelityProgressClient }) {
  const { page } = useBoard()
  const editor = page.board.fidelityShown(progress.fidelity.slug)?.editor
  if (!editor) return null
  const hint = ticket.worktree ? `Open the ${editor.label} editor on this ticket's stories` : `Activate this ticket to open it in the ${editor.label} editor`
  return (
    <button className="help-link editor-widget" title={hint} aria-label={`Open in ${editor.label}`} disabled={!ticket.worktree} onClick={() => void page.editorApp.openOn(page.editorApp.editorOf(editor), ticket.worktree, ticket.workingChat?.id)}>
      ✎
    </button>
  )
}

function TileHeadingView(props: TileProps) {
  const { ticket, progress, hasPracticeChip } = props
  const { page } = useBoard()
  const practice = page.board.practiceNamed(progress.practice.key)
  const { key, label } = progress.look
  return (
    <div className="tile-heading">
      {hasPracticeChip ? <span className="practice-chip" style={{ borderLeftColor: practice?.color }}>{practice?.name}</span> : null}
      <TileNameView {...props} />
      <span className="visually-hidden">{label}</span>
      {key === 'done' ? <CheckIcon /> : null}
      {key === 'violations' ? (
        <button className="violations-link" onClick={() => void page.panels.openReport(ticket, progress)}>
          violations
        </button>
      ) : null}
      <EditorWidgetView ticket={ticket} progress={progress} />
      <TileHelpView progress={progress} />
    </div>
  )
}

export function TileView(props: TileProps) {
  const { ticket, stage, progress, opensOnHover } = props
  const { fidelity } = progress
  const slug = fidelity.slug
  const { page } = useBoard()
  const practice = page.board.practiceNamed(progress.practice.key)
  const isOn = progress.isEnabled
  const place = cellPlace(stage.name, fidelity)
  const { key } = progress.look
  const borderColor = key === 'violations' ? 'var(--violations)' : progress.isNext ? 'var(--accent)' : 'var(--border)'
  const hover = isOn && opensOnHover ? { onMouseEnter: () => page.tiles.hoverIn({ ticket, stage, place, fidelities: [fidelity] }), onMouseLeave: () => page.tiles.hoverOut(ticket.name, place) } : {}
  const open = isOn ? page.tiles.openOn(ticket.name, place) : undefined
  return (
    <div className="skill-cell" data-tile={slug} {...hover} style={{ opacity: progress.light, borderColor, borderLeftColor: practice?.color, borderLeftWidth: key === 'done' ? DONE_EDGE_PIXELS : EDGE_PIXELS }}>
      <TileHeadingView {...props} />
      {open ? <ActionBarView ticket={ticket} tile={open} /> : null}
    </div>
  )
}
