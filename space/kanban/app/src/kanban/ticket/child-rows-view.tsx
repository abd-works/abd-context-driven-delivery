import { useBoard } from '../shared/board-context'
import { useCardDrag } from './card-drag'
import { withoutSelecting } from '../shared/card-field-view'
import { EditTextView } from './card-upkeep-view'
import type { TicketClient } from './ticket-client'

const childCount = (count: number): string => `${count} ${count === 1 ? 'child' : 'children'}`

// A child stacked in its parent's card: its title only, since its state is its parent's, and its text as its tooltip.
// It drags like a card: out onto a column, onto another ticket, or Alt-dragged off its parent.
function StackedRowView({ child }: { child: TicketClient }) {
  const { state } = useBoard()
  const { shownDrop, handlers } = useCardDrag(child)
  const shape = ['child-row', shownDrop === 'child' ? 'is-drop-over' : '', state.dragged === child.address ? 'is-dragged' : ''].filter(Boolean).join(' ')
  return (
    <div className={shape} data-child={child.name} title={child.text} draggable {...handlers} onClick={withoutSelecting(() => child.choose())}>
      <span className="child-row-title">{child.title}</span>
      <EditTextView ticket={child} />
    </div>
  )
}

// A child pulled out of its parent moves as a card of its own; its parent keeps a dashed row for it.
function PulledOutRowView({ child }: { child: TicketClient }) {
  return (
    <div className="child-row is-pulled-out" data-child={child.name} title={child.text} onClick={withoutSelecting(() => child.choose())}>
      <span className="child-row-title">{child.title}</span>
    </div>
  )
}

// A parent's children, stacked inside its card under a line that folds them away or shows them again.
export function ChildRowsView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const children = ticket.childTickets
  if (!children.length) return null
  const isShown = page.cards.showsChildrenOf(ticket)
  return (
    <div className="child-rows">
      <button className="children-toggle" aria-expanded={isShown} onClick={withoutSelecting(() => page.cards.toggleChildrenOf(ticket))}>
        {`${isShown ? '-' : '+'} ${childCount(children.length)}`}
      </button>
      {isShown ? children.map(child => (child.isPulledOut ? <PulledOutRowView key={child.name} child={child} /> : <StackedRowView key={child.name} child={child} />)) : null}
    </div>
  )
}
