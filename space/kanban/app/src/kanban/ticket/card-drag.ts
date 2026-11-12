import { useState } from 'react'
import type { DragEvent } from 'react'

import type { BacklogItemClient } from '../backlog-item/backlog-item-client'
import { useBoard } from '../shared/board-context'
import type { TicketClient } from './ticket-client'

// How far into a card from its top edge a dragged ticket of the same column is put above it, rather than made its child.
const BEFORE_EDGE_PIXELS = 12

// Dragging a card, or a child's row in its parent's card, marks its ticket as the one dragged; an opened card closes when
// the drag ends. A row takes its own drag, so the parent card it sits in does not start one as well.
function useDragSource(ticket: TicketClient) {
  const { page } = useBoard()
  const onDragStart = (event: DragEvent) => {
    event.stopPropagation()
    event.dataTransfer.setData('text/plain', ticket.name)
    event.dataTransfer.effectAllowed = 'move'
    page.store.change({ dragged: ticket.address })
  }
  const onDragEnd = () => page.store.change(current => ({ dragged: null, openCard: current.openCard === ticket.name ? null : current.openCard }))
  return { onDragStart, onDragEnd }
}

// What is being dragged, read when each event arrives, not from the last drawing: a quick drag reaches the card before
// the page redraws.
function useDragged(): () => { ticket?: TicketClient; item?: BacklogItemClient } {
  const { page } = useBoard()
  return () => {
    const address = page.store.state.dragged
    const ticket = page.board.ticketAt(address)
    return ticket ? { ticket } : { item: page.board.backlogItems.find(entry => entry.address === address) }
  }
}

// What a drop over this card would do: put the dragged ticket above it in their column, near its top edge; make the
// dragged ticket its child, where Python names it a parent choice; or start a dragged backlog item as its child.
type Drop = { kind: 'before'; ticket: TicketClient } | { kind: 'child'; ticket: TicketClient } | { kind: 'item'; item: BacklogItemClient }

export type DropKind = Drop['kind']

function useDropOver(ticket: TicketClient): (event: DragEvent) => Drop | undefined {
  const dragged = useDragged()
  return event => {
    const { ticket: other, item } = dragged()
    if (item) return ticket.isMain ? undefined : { kind: 'item', item }
    if (!other) return undefined
    if (isPlacedAbove(ticket, other, event)) return { kind: 'before', ticket: other }
    return ticket.canTakeAsChild(other) ? { kind: 'child', ticket: other } : undefined
  }
}

// Only cards of their own keep a place in a column; a stacked child goes where its parent's card is.
function isPlacedAbove(ticket: TicketClient, other: TicketClient, event: DragEvent): boolean {
  if (ticket.isStacked || other.isStacked || other.name === ticket.name || other.column.name !== ticket.column.name) return false
  return event.clientY - event.currentTarget.getBoundingClientRect().top < BEFORE_EDGE_PIXELS
}

function dropped(ticket: TicketClient, drop: Drop): Promise<unknown> {
  if (drop.kind === 'before') return drop.ticket.moveBefore(ticket.name)
  if (drop.kind === 'child') return drop.ticket.reassignParent(ticket.name)
  return drop.item.startUnder(ticket.name)
}

// The card takes the event, so the card or list under it does not act on the drop as well.
const takeHere = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()
}

// A ticket dragged onto a card is put above it or taken as its child; what a drop would do lights the card.
function useCardDrop(ticket: TicketClient) {
  const { page } = useBoard()
  const [shownDrop, setShownDrop] = useState<DropKind | null>(null)
  const dropOver = useDropOver(ticket)
  const onDragOver = (event: DragEvent) => {
    const drop = dropOver(event)
    if (!drop) return setShownDrop(null)
    takeHere(event)
    setShownDrop(drop.kind)
  }
  const onDrop = (event: DragEvent) => {
    setShownDrop(null)
    const drop = dropOver(event)
    if (!drop) return
    takeHere(event)
    page.store.change({ dragged: null })
    void dropped(ticket, drop)
  }
  return { shownDrop, onDragOver, onDragLeave: () => setShownDrop(null), onDrop }
}

// A card's, or a child row's, drag and drop: the handlers its element takes, and what a drop over it would do.
export function useCardDrag(ticket: TicketClient) {
  const source = useDragSource(ticket)
  const { shownDrop, ...target } = useCardDrop(ticket)
  return { shownDrop, handlers: { ...source, ...target } }
}

// A child stacked in its parent's card, dropped on a column's list, leaves its parent's card: pulled out, it moves as a
// card of its own and keeps its parent; Alt-dragged out, it is no longer a child at all.
export function leaveParent(child: TicketClient, event: DragEvent): Promise<unknown> {
  return event.altKey ? child.reassignParent() : child.pullOut()
}
