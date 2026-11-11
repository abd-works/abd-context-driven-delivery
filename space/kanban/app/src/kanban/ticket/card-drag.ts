import { useState } from 'react'
import type { DragEvent } from 'react'

import { useBoard } from '../shared/board-context'
import type { TicketClient } from './ticket-client'

// Dragging a card marks its ticket as the one dragged; an opened card closes when the drag ends.
function useDragSource(ticket: TicketClient) {
  const { page } = useBoard()
  const onDragStart = (event: DragEvent) => {
    event.dataTransfer.setData('text/plain', ticket.name)
    event.dataTransfer.effectAllowed = 'move'
    page.store.change({ dragged: ticket.address })
  }
  const onDragEnd = () => page.store.change(current => ({ dragged: null, openCard: current.openCard === ticket.name ? null : current.openCard }))
  return { onDragStart, onDragEnd }
}

// The ticket being dragged when it can become this ticket's child. Read when each event arrives, not from the last
// drawing: a quick drag reaches the card before the page redraws.
function useDraggedChild(ticket: TicketClient): () => TicketClient | undefined {
  const { page } = useBoard()
  return () => {
    const dragged = page.board.tickets.find(entry => entry.address === page.store.state.dragged)
    return dragged && ticket.canTakeAsChild(dragged) ? dragged : undefined
  }
}

// The card takes the event, so the list under it does not move the ticket to its column as well.
const takeHere = (event: DragEvent) => {
  event.preventDefault()
  event.stopPropagation()
}

// A ticket dragged onto a card it can become the child of is taken as that ticket's child.
function useChildDrop(ticket: TicketClient) {
  const { page } = useBoard()
  const [isTakingChild, setTakingChild] = useState(false)
  const draggedChild = useDraggedChild(ticket)
  const onDragOver = (event: DragEvent) => {
    if (!draggedChild()) return
    takeHere(event)
    setTakingChild(true)
  }
  const onDrop = (event: DragEvent) => {
    setTakingChild(false)
    const dragged = draggedChild()
    if (!dragged) return
    takeHere(event)
    page.store.change({ dragged: null })
    void ticket.takeAsChild(dragged)
  }
  return { isTakingChild, onDragOver, onDragLeave: () => setTakingChild(false), onDrop }
}

// A card's drag and drop: the handlers its element takes, and whether a ticket dragged over it would become its child.
export function useCardDrag(ticket: TicketClient) {
  const source = useDragSource(ticket)
  const { isTakingChild, ...target } = useChildDrop(ticket)
  return { isTakingChild, handlers: { ...source, ...target } }
}
