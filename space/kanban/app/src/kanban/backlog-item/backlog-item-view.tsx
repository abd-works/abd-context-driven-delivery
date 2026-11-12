import { openingOf } from '../shared/text-opening'
import { useState } from 'react'
import type { DragEvent, FormEvent, MouseEvent } from 'react'

import { ageOf } from '../shared/board-brand'
import { useBoard } from '../shared/board-context'
import { useTypedField, withoutSelecting } from '../shared/card-field-view'
import type { CardField } from '../shared/card-field-view'
import { SessionActionIcon } from '../shared/icons'
import type { BacklogItemClient, ItemDrop } from './backlog-item-client'

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

const DROP_LOOKS: Record<ItemDrop, string> = { before: 'is-drop-before', after: 'is-drop-after', child: 'is-drop-over' }

// Another backlog item dragged onto this one goes above it near its top edge, below it near its bottom edge, and in the
// middle becomes its child. Read when each event arrives, not from the last drawing: a quick drag reaches the card
// before the page redraws.
function useItemDrop(backlogItem: BacklogItemClient) {
  const { page } = useBoard()
  const [shownDrop, setShownDrop] = useState<ItemDrop | null>(null)
  const dropAt = (event: DragEvent) => {
    const dragged = page.board.backlogItems.find(entry => entry.address === page.store.state.dragged)
    if (!dragged) return undefined
    const box = event.currentTarget.getBoundingClientRect()
    const drop = backlogItem.dropOf(dragged, (event.clientY - box.top) / Math.max(box.height, 1))
    return drop ? { dragged, drop } : undefined
  }
  const onDragOver = (event: DragEvent) => {
    const found = dropAt(event)
    setShownDrop(found?.drop ?? null)
    if (!found) return
    event.preventDefault()
    event.stopPropagation()
  }
  const onDrop = (event: DragEvent) => {
    setShownDrop(null)
    const found = dropAt(event)
    if (!found) return
    event.preventDefault()
    event.stopPropagation()
    page.store.change({ dragged: null })
    void backlogItem.take(found.dragged, found.drop)
  }
  return { shownDrop, onDragOver, onDragLeave: () => setShownDrop(null), onDrop }
}

function useItemDrag(backlogItem: BacklogItemClient) {
  const { page } = useBoard()
  const onDragStart = (event: DragEvent) => {
    // A child's row takes its own drag, so the parent card it sits in does not start one as well.
    event.stopPropagation()
    event.dataTransfer.setData('text/plain', backlogItem.title)
    event.dataTransfer.effectAllowed = 'move'
    page.store.change({ dragged: backlogItem.address })
  }
  return { onDragStart, onDragEnd: () => page.store.change({ dragged: null }) }
}

const EDIT_ITEM_TEXT: CardField = { action: 'text', label: 'Edit text', hint: 'Edit what this idea is about', field: 'Item text', placeholder: 'Text, then Enter' }

// The most lines the text box grows to before it scrolls.
const EDITOR_MOST_LINES = 10

// The item's text, shown only on its selected card and cut to its opening paragraphs, since the details bar shows it
// whole. Edit text opens a box in the text's place, holding the whole text, which Enter writes back to its file.
function ItemTextView({ item, isSelected }: { item: BacklogItemClient; isSelected: boolean }) {
  const { typed, setTyped, pressed } = useTypedField(text => item.editText(text))
  const { opening, isCut } = openingOf(item.text)
  if (typed !== null) {
    const rows = Math.min(Math.max(typed.split('\n').length, 3), EDITOR_MOST_LINES)
    return (
      <div className="item-text-line">
        <textarea className="card-field item-text-editor" aria-label={EDIT_ITEM_TEXT.field} placeholder="Text; Enter saves, Shift+Enter adds a line" rows={rows} value={typed} autoFocus onClick={event => event.stopPropagation()} onChange={event => setTyped(event.target.value)} onKeyDown={pressed} onBlur={() => setTyped(null)} />
      </div>
    )
  }
  return (
    <div className="item-text-line">
      {isSelected && item.text ? <div className="ticket-text">{opening}</div> : null}
      {isSelected && isCut ? <div className="ticket-text-more">More in {item.path}</div> : null}
      <button className="file-view" aria-label={EDIT_ITEM_TEXT.label} title={EDIT_ITEM_TEXT.hint} onClick={withoutSelecting(() => setTyped(item.text))}>
        <SessionActionIcon action={EDIT_ITEM_TEXT.action} />
      </button>
    </div>
  )
}

// A child kept in its parent's folder: a row in its parent's card, its text as its tooltip. It drags like a card: onto
// another card, or out onto the Backlog, where it is an item of its own again.
function ChildItemRowView({ child }: { child: BacklogItemClient }) {
  const { state } = useBoard()
  const shape = ['child-row', state.dragged === child.address ? 'is-dragged' : ''].filter(Boolean).join(' ')
  const select = (event: MouseEvent) => {
    event.stopPropagation()
    child.select()
  }
  return (
    <div className={shape} data-child-item={child.title} title={child.text} draggable {...useItemDrag(child)} onClick={select}>
      <span className="child-row-title">{child.title}</span>
    </div>
  )
}

function ChildItemRowsView({ item }: { item: BacklogItemClient }) {
  if (!item.childItems.length) return null
  return (
    <div className="child-rows">
      {item.childItems.map(child => (
        <ChildItemRowView key={child.path} child={child} />
      ))}
    </div>
  )
}

// A backlog item starts when it is dragged into Discovery's In progress; dragged onto another it goes above it, below
// it, or inside it as its child.
export function BacklogCardView({ item }: { item: BacklogItemClient }) {
  const { page, state } = useBoard()
  const isSelected = page.board.selectedItem?.title === item.title
  const { shownDrop, ...drop } = useItemDrop(item)
  const className = ['ticket-card', item.childItems.length ? 'is-parent' : '', state.dragged === item.address ? 'is-dragged' : '', shownDrop ? DROP_LOOKS[shownDrop] : ''].filter(Boolean).join(' ')
  return (
    <div className={className} data-item={item.title} draggable {...useItemDrag(item)} {...drop} onClick={() => item.select()} style={{ borderColor: isSelected ? 'var(--text)' : 'var(--border)' }}>
      {/* Chrome starts no drag on a button, and this one covers the card, so it carries the card's drag. */}
      <button className="card-hit" aria-label={`Show ${item.title}`} draggable />
      <span className="expand-mark card-mark" aria-hidden="true" />
      <div className="ticket-title">{item.title}</div>
      <div className="ticket-meta">{ageOf(state.now, item.lastActivity)}</div>
      <ItemTextView item={item} isSelected={isSelected} />
      <ChildItemRowsView item={item} />
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
