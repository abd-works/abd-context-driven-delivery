import type { FormEvent } from 'react'

import { ageOf } from '../board/board-brand'
import { useBoard } from '../board/board-context'
import type { BacklogItemClient } from './backlog-item-client'

export function ComposerView() {
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

export function BacklogCardView({ item }: { item: BacklogItemClient }) {
  const { page, state } = useBoard()
  const isSelected = page.board.selectedItem?.title === item.title
  return (
    <div className="ticket-card" data-item={item.title} onClick={() => item.select()} style={{ borderColor: isSelected ? 'var(--text)' : 'var(--border)' }}>
      <button className="card-hit" aria-label={`Show ${item.title}`} />
      <span className="expand-mark card-mark" aria-hidden="true" />
      <div className="ticket-title">{item.title}</div>
      <div className="ticket-meta">{ageOf(state.now, item.lastActivity)}</div>
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

export function ItemBarView() {
  const { page } = useBoard()
  const item = page.board.selectedItem
  if (!item) return null
  return (
    <div className="details-bar-words">
      <div className="details-heading">
        <div className="details-title">
          <h2>{item.title}</h2>
          <span className="details-place">{item.path}</span>
        </div>
        {item.text ? <p className="item-text">{item.text}</p> : null}
      </div>
      <button className="action primary" onClick={() => void item.start()}>
        Start
      </button>
    </div>
  )
}
