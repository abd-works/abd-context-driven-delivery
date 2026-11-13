import { useEffect, useState } from 'react'
import type { DragEvent, KeyboardEvent, ReactNode } from 'react'

import type { BacklogItemClient } from '../backlog-item/backlog-item-client'
import { BacklogCardView, ComposerView } from '../backlog-item/backlog-item-view'
import { leaveParent } from '../ticket/card-drag'
import { TicketCardView } from '../ticket/ticket-card-view'
import type { CardSpot } from '../ticket/ticket-card-view'
import type { TicketClient } from '../ticket/ticket-client'
import { useBoard } from '../shared/board-context'
import type { ColumnClient } from './column-client'
import { StageHeadView } from '../shared/stage-head-view'

function WipLimitFieldView({ column }: { column: ColumnClient }) {
  const { page } = useBoard()
  const [text, setText] = useState(String(column.wipLimit))
  const submit = () => void column.submitWipLimit(text)
  const pressed = (event: KeyboardEvent) => {
    if (event.key === 'Enter') submit()
    if (event.key === 'Escape') page.layout.cancelLimit()
  }
  return <input type="number" min="1" className="limit-field" aria-label={`WIP limit for ${column.name}`} value={text} onChange={event => setText(event.target.value)} onBlur={submit} onKeyDown={pressed} autoFocus />
}

function WipLimitView({ column }: { column: ColumnClient }) {
  const { page, state } = useBoard()
  const limit = column.wipLimit
  return (
    <span className={column.isOverLimit ? 'stage-count is-over-limit' : 'stage-count'}>
      <span>{column.count}</span>
      <span>/</span>
      {state.editingLimit === column.name ? (
        <WipLimitFieldView column={column} />
      ) : (
        <button className="limit-button" aria-label={`WIP limit for ${column.name} is ${limit}. Edit`} title="Edit WIP limit" onClick={() => page.layout.editLimit(column.name)}>
          {limit}
        </button>
      )}
    </span>
  )
}

function EdgeHeadView({ column }: { column: ColumnClient }) {
  const { page } = useBoard()
  return (
    <div className="edge-head">
      <span>{column.name.toUpperCase()}</span>
      <span className="edge-count">
        <span>{column.count}</span>
        {column.isBacklog ? (
          <button className="icon-button add-item" aria-label="New backlog ticket" title="New backlog ticket" onClick={() => page.draft.open()}>
            +
          </button>
        ) : null}
      </span>
    </div>
  )
}

function EdgeColumnView({ column }: { column: ColumnClient }) {
  const { state } = useBoard()
  return (
    <div className="board-column" data-column={column.name}>
      <EdgeHeadView column={column} />
      {column.isBacklog && state.draft.isOpen ? <ComposerView /> : null}
      <div className="card-lists is-single">
        <DropZoneView className="card-list" accepts={ticket => ticket.canDropOn(column.name)} onDrop={ticket => ticket.dropOn(column.name)}>
          {column.items.map(item => (
            <BacklogCardView key={item.path} item={item} />
          ))}
          <TicketListView tickets={column.tickets} spot="only" />
        </DropZoneView>
      </div>
    </div>
  )
}

type DropProps = {
  accepts: (ticket: TicketClient) => boolean
  onDrop: (ticket: TicketClient) => unknown
  onItemDrop?: (item: BacklogItemClient) => unknown
  className: string
  children: ReactNode
}

// A list a dragged card can be dropped on. Only a list that would change where the card is accepts it, and only a list
// given onItemDrop takes a backlog item. Any list takes a child dragged out of its parent's card, which leaves it there.
function DropZoneView({ accepts, onDrop, onItemDrop, className, children }: DropProps) {
  const { page, state } = useBoard()
  const [isOver, setOver] = useState(false)
  // Read when each event arrives, not from the last drawing: a quick drag reaches the list before the page redraws.
  const draggedNow = () => {
    const address = page.store.state.dragged
    const ticket = page.board.ticketAt(address)
    const item = onItemDrop ? page.board.backlogItems.find(entry => entry.address === address) : undefined
    return { ticket, item, isAccepted: (ticket !== undefined && (ticket.isStacked || accepts(ticket))) || item !== undefined }
  }
  const isAccepted = state.dragged !== null && draggedNow().isAccepted
  const draggedOver = (event: DragEvent) => {
    if (!draggedNow().isAccepted) return
    event.preventDefault()
    setOver(true)
  }
  const dropped = (event: DragEvent) => {
    event.preventDefault()
    setOver(false)
    const { ticket, item, isAccepted: wasAccepted } = draggedNow()
    page.store.change({ dragged: null })
    if (item && onItemDrop) void onItemDrop(item)
    else if (ticket?.isStacked) void leaveParent(ticket, event)
    else if (ticket && wasAccepted) void onDrop(ticket)
  }
  const shown = [className, isAccepted ? 'is-drop-zone' : '', isAccepted && isOver ? 'is-drop-over' : ''].filter(Boolean).join(' ')
  return (
    <div className={shown} onDragOver={draggedOver} onDragLeave={() => setOver(false)} onDrop={dropped}>
      {children}
    </div>
  )
}

// Starting a backlog item opens it in the first stage's In progress, so only that list takes one.
function StageListView({ column, done, children }: { column: ColumnClient; done: boolean; children: ReactNode }) {
  const { page } = useBoard()
  const accepts = (ticket: TicketClient) => !(ticket.column.name === column.name && ticket.isDone === done)
  const startsItems = !done && page.board.stages[0]?.name === column.name
  return (
    <DropZoneView className="card-list" accepts={accepts} onDrop={ticket => ticket.moveTo(column.name, done)} onItemDrop={startsItems ? item => page.roots.openToStart(item) : undefined}>
      {children}
    </DropZoneView>
  )
}

function TicketListView({ tickets, spot }: { tickets: TicketClient[]; spot: CardSpot }) {
  return (
    <>
      {tickets.map(ticket => (
        <TicketCardView key={ticket.address} ticket={ticket} spot={spot} />
      ))}
    </>
  )
}

function StageColumnView({ column }: { column: ColumnClient }) {
  return (
    <div className="board-column" data-column={column.name}>
      <div className="stage-head-box">
        <StageHeadView stage={column} isOverLimit={column.isOverLimit}>
          <WipLimitView column={column} />
        </StageHeadView>
      </div>
      <div className="card-lists">
        <StageListView column={column} done={false}>
          <span className="list-label">IN PROGRESS</span>
          <TicketListView tickets={column.inProgress} spot="left" />
        </StageListView>
        <StageListView column={column} done>
          <span className="list-label">DONE</span>
          <TicketListView tickets={column.done} spot="right" />
        </StageListView>
      </div>
    </div>
  )
}

function WaitingView({ hasFailed }: { hasFailed: boolean }) {
  return <p className="board-waiting">{hasFailed ? 'No columns while the server is not answering: the board appears here once it does.' : 'Reading the board…'}</p>
}

export function BoardColumnsView() {
  const { page, state } = useBoard()
  useKeptSelection()
  return (
    <section className="board-region" aria-label="Board" style={{ flexBasis: state.expandedRegion ? 0 : state.boardHeight, flexGrow: state.expandedRegion ? 1 : 0 }}>
      {state.board && !state.serverFailure ? (
        <div className="column-grid">
          {page.board.shownColumns.map(column => (column.isStage ? <StageColumnView key={column.name} column={column} /> : <EdgeColumnView key={column.name} column={column} />))}
        </div>
      ) : (
        <WaitingView hasFailed={state.serverFailure !== null} />
      )}
    </section>
  )
}

// A ticket can leave its column between reads, by a move made in the chat, so an open card lets go of a ticket that is gone.
function useKeptSelection(): void {
  const { page, state } = useBoard()
  const isGone = state.board !== null && state.openCard !== null && !page.board.tickets.some(ticket => ticket.name === state.openCard)
  useEffect(() => {
    if (isGone && state.openCard) page.cards.releaseTicket(state.openCard)
  }, [isGone, page, state.openCard])
}
