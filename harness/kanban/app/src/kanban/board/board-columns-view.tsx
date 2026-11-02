import { useEffect, useState } from 'react'
import type { KeyboardEvent } from 'react'

import { BacklogCardView, ComposerView } from '../backlog-item/backlog-item-view'
import { TicketCardView } from '../ticket/ticket-card-view'
import type { CardSpot } from '../ticket/ticket-card-view'
import type { TicketClient } from '../ticket/ticket-client'
import { useBoard } from './board-context'
import type { ColumnClient } from './column-client'
import { StageHeadView } from './stage-head-view'

function WipLimitFieldView({ column }: { column: ColumnClient }) {
  const { page } = useBoard()
  const [text, setText] = useState(String(column.wipLimit))
  const submit = () => void page.board.setWipLimit(column.name, text)
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
        <div className="card-list">
          {column.items.map(item => (
            <BacklogCardView key={item.path} item={item} />
          ))}
          <TicketListView tickets={column.tickets} spot="only" />
        </div>
      </div>
    </div>
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
        <StageHeadView stage={column.name} isOverLimit={column.isOverLimit}>
          <WipLimitView column={column} />
        </StageHeadView>
      </div>
      <div className="card-lists">
        <div className="card-list">
          <span className="list-label">IN PROGRESS</span>
          <TicketListView tickets={column.inProgress} spot="left" />
        </div>
        <div className="card-list">
          <span className="list-label">DONE</span>
          <TicketListView tickets={column.done} spot="right" />
        </div>
      </div>
    </div>
  )
}

function WaitingView({ hasFailed }: { hasFailed: boolean }) {
  return <p className="board-waiting">{hasFailed ? 'Connect the cdd server and the board appears here.' : 'Reading the board…'}</p>
}

export function BoardColumnsView() {
  const { page, state } = useBoard()
  useKeptSelection()
  return (
    <section className="board-region" aria-label="Board" style={{ flexBasis: state.expandedRegion ? 0 : state.boardHeight, flexGrow: state.expandedRegion ? 1 : 0 }}>
      {state.board ? (
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
