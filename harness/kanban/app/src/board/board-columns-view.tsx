import { useEffect, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'

import type { BacklogItem, Column, Ticket } from './board'
import { ageOf } from './board-brand'
import { useBoard } from './board-context'
import { StageHeadView } from './stage-head-view'
import { TicketCardView } from './ticket-card-view'
import type { CardSpot } from './ticket-card-view'

function WipLimitFieldView({ column }: { column: Column }) {
  const { page } = useBoard()
  const [text, setText] = useState(String(column.wip_limit))
  const submit = () => void page.board.submitLimit(column.name, text)
  const pressed = (event: KeyboardEvent) => {
    if (event.key === 'Enter') submit()
    if (event.key === 'Escape') page.board.cancelLimit()
  }
  return <input type="number" min="1" className="limit-field" aria-label={`WIP limit for ${column.name}`} value={text} onChange={event => setText(event.target.value)} onBlur={submit} onKeyDown={pressed} autoFocus />
}

function WipLimitView({ column }: { column: Column }) {
  const { page, state } = useBoard()
  const limit = column.wip_limit
  return (
    <span className={column.is_over_limit ? 'stage-count is-over-limit' : 'stage-count'}>
      <span>{page.board.countOf(column)}</span>
      <span>/</span>
      {state.editingLimit === column.name ? (
        <WipLimitFieldView column={column} />
      ) : (
        <button className="limit-button" aria-label={`WIP limit for ${column.name} is ${limit}. Edit`} title="Edit WIP limit" onClick={() => page.board.editLimit(column.name)}>
          {limit}
        </button>
      )}
    </span>
  )
}

function ComposerView() {
  const { page, state } = useBoard()
  const { title, text } = state.draft
  const submit = (event: FormEvent) => {
    event.preventDefault()
    void page.draft.add()
  }
  return (
    <form className="composer" onSubmit={submit}>
      <input aria-label="Title" placeholder="Title" value={title} onChange={event => page.draft.type('title', event.target.value)} autoFocus />
      <textarea aria-label="Text" placeholder="Text" rows={5} value={text} onChange={event => page.draft.type('text', event.target.value)} />
      <div className="composer-actions">
        <button className="action primary small" type="submit" disabled={!title.trim()}>
          Add
        </button>
        <button className="action small" type="button" onClick={() => page.draft.cancel()}>
          Cancel
        </button>
      </div>
    </form>
  )
}

function BacklogCardView({ json }: { json: BacklogItem }) {
  const { page, state } = useBoard()
  const item = page.item(json)
  const isSelected = page.board.selectedItem?.title === item.title
  return (
    <div className="ticket-card" data-item={item.title} onClick={() => item.select()} style={{ borderColor: isSelected ? 'var(--text)' : 'var(--border)' }}>
      <button className="card-hit" aria-label={`Show ${item.title}`} />
      <div className="ticket-title">{item.title}</div>
      <div className="ticket-meta">{ageOf(state.now, item.last_activity)}</div>
      <div className="start-line">
        <button className="action card-move" aria-label={`Move ${item.title} into Discovery`} title={`Move ${item.title} into Discovery`} onClick={event => {
            event.stopPropagation()
            void item.start()
          }}>
          →
        </button>
      </div>
    </div>
  )
}

function EdgeColumnView({ column }: { column: Column }) {
  const { page, state } = useBoard()
  const isBacklog = Boolean(column.items)
  return (
    <div className="board-column" data-column={column.name}>
      <div className="edge-head">
        <span>{column.name.toUpperCase()}</span>
        <span className="edge-count">
          <span>{page.board.countOf(column)}</span>
          {isBacklog ? (
            <button className="icon-button add-item" aria-label="New backlog ticket" title="New backlog ticket" onClick={() => page.draft.open()}>
              +
            </button>
          ) : null}
        </span>
      </div>
      {isBacklog && state.draft.isOpen ? <ComposerView /> : null}
      <div className="card-lists is-single">
        <div className="card-list">
          {(column.items ?? []).map(item => (
            <BacklogCardView key={item.path} json={item} />
          ))}
          <TicketListView tickets={column.tickets ?? []} spot="only" />
        </div>
      </div>
    </div>
  )
}

function TicketListView({ tickets, spot }: { tickets: Ticket[]; spot: CardSpot }) {
  const { page } = useBoard()
  return (
    <>
      {tickets.map(ticket => (
        <TicketCardView key={`${ticket.column}/${ticket.name}`} ticket={page.ticket(ticket)} spot={spot} />
      ))}
    </>
  )
}

function StageColumnView({ column }: { column: Column }) {
  return (
    <div className="board-column" data-column={column.name}>
      <div className="stage-head-box">
        <StageHeadView stage={column.name} isOverLimit={column.is_over_limit}>
          <WipLimitView column={column} />
        </StageHeadView>
      </div>
      <div className="card-lists">
        <div className="card-list">
          <span className="list-label">IN PROGRESS</span>
          <TicketListView tickets={column.in_progress ?? []} spot="left" />
        </div>
        <div className="card-list">
          <span className="list-label">DONE</span>
          <TicketListView tickets={column.done ?? []} spot="right" />
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
          {page.board.columns.map(column => (column.work_required ? <StageColumnView key={column.name} column={column} /> : <EdgeColumnView key={column.name} column={column} />))}
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
    if (isGone && state.openCard) page.tiles.releaseTicket(state.openCard)
  }, [isGone, page, state.openCard])
}
