import { useEffect, useRef, useState } from 'react'
import type { DragEvent, MouseEvent, RefObject } from 'react'

import { ageOf, practiceOf } from '../board/board-brand'
import { useBoard } from '../board/board-context'
import type { ColumnClient } from '../board/column-client'
import { FileViewsView } from './file-views-view'
import type { TicketClient } from './ticket-client'
import { skillOf } from './ticket-client'
import { TileView } from './tile-view'

export type CardSpot = 'left' | 'right' | 'only'

const ACTIVE_BORDER_WIDTH = 3
const OPENS_LEFT_COLUMNS = ['Implementation', 'Complete']

const withoutSelecting = (press: () => unknown) => (event: MouseEvent) => {
  event.stopPropagation()
  void press()
}

// The open card covers the closed one from the same corner and grows out to the width of a tile in the details.
// Sizes are from the card's edge: the card's border, the list's 8px padding and the column's 1px border.
function openCardPlace(ticket: TicketClient, spot: CardSpot) {
  const border = ticket.isActive ? ACTIVE_BORDER_WIDTH : 1
  const span = spot === 'only' ? `100% + ${2 * (9 + border)}px` : `200% + ${4 * border + 26}px`
  const opensLeft = OPENS_LEFT_COLUMNS.includes(ticket.column)
  return { width: `calc(${span})`, top: -border, left: opensLeft ? 'auto' : -border, right: opensLeft ? -border : 'auto', opensLeft }
}

function SegmentsView({ ticket, stage, onSkill }: { ticket: TicketClient; stage: ColumnClient; onSkill: (skill: string) => void }) {
  const { page, state } = useBoard()
  return (
    <div className="segments">
      {ticket.enabledSlugs(stage).map(slug => {
        const { key, label, color } = ticket.stateOf(slug)
        const skill = skillOf(slug)
        const isOpen = state.tile?.ticket === ticket.name && state.tile.slugs.length === 1 && state.tile.slugs[0] === slug
        const leave = () => onSkill('')
        const enter = () => onSkill(skill)
        const background = key === 'violations' ? color : practiceOf(slug)?.color
        return (
          <button key={slug} className="segment-hit" title={skill} aria-label={`${skill}: ${label}`} aria-expanded={isOpen} onClick={withoutSelecting(() => page.cards.openSegment(ticket, stage, slug))} onMouseEnter={enter} onMouseLeave={leave} onFocus={enter} onBlur={leave}>
            <span className="segment" style={{ background, opacity: ticket.lightOf(slug) }} />
          </button>
        )
      })}
    </div>
  )
}

function CardMarkView({ ticket }: { ticket: TicketClient }) {
  const { page, state } = useBoard()
  const isOpen = state.openCard === ticket.name
  return (
    <button className="expand-mark card-mark" aria-label={`Actions for ${ticket.title}`} aria-expanded={isOpen} onClick={withoutSelecting(() => page.cards.toggle(ticket))}>
      {isOpen ? '▴' : '▾'}
    </button>
  )
}

function CardFaceView({ ticket, stage }: { ticket: TicketClient; stage: ColumnClient }) {
  const { page, state } = useBoard()
  const [skill, setSkill] = useState('')
  return (
    <>
      <CardMarkView ticket={ticket} />
      <div className="ticket-title">{ticket.title}</div>
      <div className="ticket-meta">{ageOf(state.now, ticket.lastActivity)}</div>
      <SegmentsView ticket={ticket} stage={stage} onSkill={setSkill} />
      {skill ? <div className="card-skill">{skill}</div> : null}
      {ticket.violatedSlugs.length ? (
        <button className="violations-link card-violations" onClick={withoutSelecting(() => page.panels.openReport(ticket.name, ''))}>
          violations
        </button>
      ) : null}
      <div className="card-files">
        <FileViewsView ticket={ticket.name} slugs={ticket.enabledSlugs(stage)} />
      </div>
    </>
  )
}

function MoveRowView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  return (
    <div className="card-moves">
      <button className="action card-activate" disabled={ticket.isClosed} onClick={withoutSelecting(() => page.activation.start(ticket, ticket.isActive))}>
        {ticket.isActive ? 'Close' : 'Activate'}
      </button>
    </div>
  )
}

const ROOM_BELOW_OPEN_CARD = 8

// The open card floats over the board, so the columns would stop short of it. Every column grows to reach its bottom
// while it is open, and they stay the same height as each other because the grid stretches them all.
function useColumnsReachOpenCard(card: RefObject<HTMLDivElement | null>): void {
  useEffect(() => {
    const open = card.current
    const grid = open?.closest<HTMLElement>('.column-grid')
    if (!open || !grid) return
    const reach = () => {
      grid.style.minHeight = `${open.getBoundingClientRect().bottom - grid.getBoundingClientRect().top + ROOM_BELOW_OPEN_CARD}px`
    }
    const watcher = new ResizeObserver(reach)
    watcher.observe(open)
    reach()
    return () => {
      watcher.disconnect()
      grid.style.minHeight = ''
    }
  }, [card])
}

// An open card shows the same tiles as the details, so a ticket can be worked from either place.
function OpenCardView({ ticket, stage, spot }: { ticket: TicketClient; stage: ColumnClient; spot: CardSpot }) {
  const { state } = useBoard()
  const card = useRef<HTMLDivElement>(null)
  const { opensLeft, ...place } = openCardPlace(ticket, spot)
  const openTile = state.tile?.ticket === ticket.name ? state.tile.place : ''
  // Braces matter: newer browsers return a promise from scrollIntoView, and React would call it as the effect's cleanup.
  useEffect(() => {
    card.current?.scrollIntoView({ block: 'nearest', inline: 'nearest' })
  }, [openTile])
  useColumnsReachOpenCard(card)
  return (
    <div ref={card} className={opensLeft ? 'card-open grows-left' : 'card-open'} data-open-card={ticket.name} style={{ ...place, borderColor: borderColorOf(ticket), borderWidth: ticket.isActive ? ACTIVE_BORDER_WIDTH : 1 }}>
      <CardFaceView ticket={ticket} stage={stage} />
      {ticket.enabledSlugs(stage).map(slug => (
        <TileView key={slug} ticket={ticket} stage={stage} slug={slug} hasPracticeChip />
      ))}
      <MoveRowView ticket={ticket} />
    </div>
  )
}

const borderColorOf = (ticket: TicketClient, isSelected = false): string => (ticket.isActive ? 'var(--accent)' : isSelected ? 'var(--text)' : 'var(--border)')

export function TicketCardView({ ticket, spot }: { ticket: TicketClient; spot: CardSpot }) {
  const { page, state } = useBoard()
  const stage = page.board.stageOf(ticket)
  const isSelected = page.board.selectedTicket?.address === ticket.address
  if (!stage) return null
  // A locked ticket cannot use its arrows, so it cannot be dragged either; an open card is being worked, not moved.
  const isDraggable = !ticket.isLocked && state.openCard !== ticket.name
  const dragStarted = (event: DragEvent) => {
    event.dataTransfer.setData('text/plain', ticket.name)
    event.dataTransfer.effectAllowed = 'move'
    page.store.change({ dragged: ticket.address })
  }
  return (
    <div
      className={['ticket-card', ticket.isActive ? 'is-active' : '', state.dragged === ticket.address ? 'is-dragged' : ''].filter(Boolean).join(' ')}
      data-ticket={ticket.name}
      draggable={isDraggable}
      onDragStart={dragStarted}
      onDragEnd={() => page.store.change({ dragged: null })}
      onClick={() => ticket.select()}
      style={{ borderColor: borderColorOf(ticket, isSelected), borderWidth: ticket.isActive ? ACTIVE_BORDER_WIDTH : 1 }}
    >
      {/* Chrome starts no drag on a button, and this one covers the card, so it carries the card's drag. */}
      <button className="card-hit" aria-label={`Show ${ticket.title}`} draggable={isDraggable} />
      <CardFaceView ticket={ticket} stage={stage} />
      {state.openCard === ticket.name ? <OpenCardView ticket={ticket} stage={stage} spot={spot} /> : null}
      <MoveRowView ticket={ticket} />
    </div>
  )
}
