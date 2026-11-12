import { useState } from 'react'
import type { DragEvent, FormEvent } from 'react'

import { ageOf } from '../shared/board-brand'
import { useBoard } from '../shared/board-context'
import { CardFieldView } from '../shared/card-field-view'
import type { CardField } from '../shared/card-field-view'
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

// Another backlog item dragged onto this one is put just above it, and the Backlog keeps that order. Read when each event
// arrives, not from the last drawing: a quick drag reaches the card before the page redraws.
function useItemDrop(backlogItem: BacklogItemClient) {
  const { page } = useBoard()
  const [isOver, setOver] = useState(false)
  const draggedItem = () => page.board.backlogItems.find(entry => entry.address === page.store.state.dragged && entry.address !== backlogItem.address)
  const onDragOver = (event: DragEvent) => {
    if (!draggedItem()) return
    event.preventDefault()
    setOver(true)
  }
  const onDrop = (event: DragEvent) => {
    setOver(false)
    const dragged = draggedItem()
    if (!dragged) return
    event.preventDefault()
    page.store.change({ dragged: null })
    void dragged.moveBefore(backlogItem.title)
  }
  return { isOver, onDragOver, onDragLeave: () => setOver(false), onDrop }
}

function useItemDrag(backlogItem: BacklogItemClient) {
  const { page } = useBoard()
  const onDragStart = (event: DragEvent) => {
    event.dataTransfer.setData('text/plain', backlogItem.title)
    event.dataTransfer.effectAllowed = 'move'
    page.store.change({ dragged: backlogItem.address })
  }
  return { onDragStart, onDragEnd: () => page.store.change({ dragged: null }) }
}

const EDIT_ITEM_TEXT: CardField = { action: 'text', label: 'Edit text', hint: 'Edit what this idea is about', field: 'Item text', placeholder: 'Text, then Enter' }

// The item's text, shown on its card and rewritten in its file from a field there.
function ItemTextView({ item }: { item: BacklogItemClient }) {
  return (
    <div className="item-text-line">
      {item.text ? <div className="ticket-text">{item.text}</div> : null}
      <CardFieldView shape={EDIT_ITEM_TEXT} isOff={false} typedAtFirst={item.text} onEnter={text => item.editText(text)} />
    </div>
  )
}

// A backlog item starts when it is dragged into Discovery's In progress, and keeps its place when dragged onto another.
export function BacklogCardView({ item }: { item: BacklogItemClient }) {
  const { page, state } = useBoard()
  const isSelected = page.board.selectedItem?.title === item.title
  const { isOver, ...drop } = useItemDrop(item)
  const className = ['ticket-card', state.dragged === item.address ? 'is-dragged' : '', isOver ? 'is-drop-before' : ''].filter(Boolean).join(' ')
  return (
    <div className={className} data-item={item.title} draggable {...useItemDrag(item)} {...drop} onClick={() => item.select()} style={{ borderColor: isSelected ? 'var(--text)' : 'var(--border)' }}>
      {/* Chrome starts no drag on a button, and this one covers the card, so it carries the card's drag. */}
      <button className="card-hit" aria-label={`Show ${item.title}`} draggable />
      <span className="expand-mark card-mark" aria-hidden="true" />
      <div className="ticket-title">{item.title}</div>
      <div className="ticket-meta">{ageOf(state.now, item.lastActivity)}</div>
      <ItemTextView item={item} />
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
      <button className="action primary" onClick={() => void page.roots.openToStart(item)}>
        Start
      </button>
    </div>
  )
}
