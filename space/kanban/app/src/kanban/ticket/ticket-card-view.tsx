import { useEffect, useRef, useState } from 'react'
import type { DragEvent, MouseEvent, RefObject } from 'react'

import { ageOf } from '../board/board-brand'
import { useBoard } from '../board/board-context'
import type { ColumnClient } from '../board/column-client'
import { SessionActionIcon } from '../board/icons'
import { FileViewsView } from './file-views-view'
import type { TicketClient } from './ticket-client'
import { TileView } from './tile-view'

export type CardSpot = 'left' | 'right' | 'only'

const ACTIVE_BORDER_WIDTH = 3

const withoutSelecting = (press: () => unknown) => (event: MouseEvent) => {
  event.stopPropagation()
  void press()
}

// The open card covers the closed one from the same corner and grows out to the width of a tile in the details.
// Sizes are from the card's edge: the card's border, the list's 8px padding and the column's 1px border.
function openCardPlace(ticket: TicketClient, spot: CardSpot, opensLeft: boolean) {
  const border = ticket.isActive ? ACTIVE_BORDER_WIDTH : 1
  const span = spot === 'only' ? `100% + ${2 * (9 + border)}px` : `200% + ${4 * border + 26}px`
  return { width: `calc(${span})`, top: -border, left: opensLeft ? 'auto' : -border, right: opensLeft ? -border : 'auto', opensLeft }
}

function SegmentsView({ ticket, stage, onSkill }: { ticket: TicketClient; stage: ColumnClient; onSkill: (skill: string) => void }) {
  const { page, state } = useBoard()
  return (
    <div className="segments">
      {ticket.progressIn(stage).map(progress => {
        const { fidelity } = progress
        const slug = fidelity.slug
        const { key, label, color } = progress.look
        const practice = page.board.practiceNamed(progress.practice.key)
        const skill = page.board.fidelityShown(slug)?.skill ?? slug
        const isOpen = state.tiles.some(tile => tile.ticket.name === ticket.name && tile.fidelities.length === 1 && tile.fidelities[0]?.slug === slug)
        const leave = () => onSkill('')
        const enter = () => onSkill(skill)
        const background = key === 'violations' ? color : practice?.color
        return (
          <button key={slug} className="segment-hit" title={label} aria-label={`${skill}: ${label}`} aria-expanded={isOpen} onClick={withoutSelecting(() => page.cards.openSegment(ticket, stage, fidelity))} onMouseEnter={enter} onMouseLeave={leave} onFocus={enter} onBlur={leave}>
            <span className="segment" style={{ background, opacity: progress.light }} />
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
      <div className="ticket-title-line">
        <div className="ticket-title">{ticket.title}</div>
        {ticket.chat.isOpening ? <span className="progress-wheel" role="status" title="Opening its chat in the Claude app" aria-label="Opening its chat" /> : null}
        <SplitActionView ticket={ticket} />
      </div>
      <div className="ticket-meta">{ageOf(state.now, ticket.lastActivity)}</div>
      <SegmentsView ticket={ticket} stage={stage} onSkill={setSkill} />
      {skill ? <div className="card-skill">{skill}</div> : null}
      {ticket.hasViolationsIn(stage) ? (
        <button className="violations-link card-violations" onClick={withoutSelecting(() => page.panels.openReport(ticket, null))}>
          violations
        </button>
      ) : null}
      <div className="card-files">
        <SessionActionsView ticket={ticket} />
        <FileViewsView ticket={ticket} progress={ticket.progressIn(stage)} />
      </div>
    </>
  )
}

function SessionActionView({ action, label, hint, isOff, onPress }: { action: string; label: string; hint: string; isOff: boolean; onPress: () => unknown }) {
  return (
    <button className="file-view" aria-label={label} title={hint} disabled={isOff} onClick={withoutSelecting(onPress)}>
      <SessionActionIcon action={action} />
    </button>
  )
}

// Split and Handoff fill the chat's prompt, so they need a chat that can take a command.
function useCannotFill(ticket: TicketClient): boolean {
  const { page } = useBoard()
  return ticket.isClosed || ticket.isLocked || !page.chat.canSend
}

function SplitActionView({ ticket }: { ticket: TicketClient }) {
  return <SessionActionView action="split" label="Split" hint="Split into child tickets, one per story" isOff={useCannotFill(ticket)} onPress={() => ticket.fillSplit()} />
}

// What a card does for its session, as icons in its bottom-left corner.
function SessionActionsView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  const cannotFill = useCannotFill(ticket)
  return (
    <span className="file-views">
      <SessionActionView action="next" label={ticket.runNextLabel} hint={ticket.runNextHint} isOff={!ticket.canRunNext} onPress={() => ticket.runNext()} />
      <SessionActionView action="handoff" label="Handoff" hint="Write a handoff for this session" isOff={cannotFill} onPress={() => ticket.fillHandoff()} />
      {ticket.isActive ? (
        <SessionActionView action="close" label="Close" hint="Close this session in the chat" isOff={cannotFill} onPress={() => ticket.closeSession()} />
      ) : (
        <SessionActionView action="activate" label="Activate" hint="Activate this session" isOff={ticket.isClosed} onPress={() => page.activation.start(ticket, false)} />
      )}
    </span>
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
  const { page, state } = useBoard()
  const card = useRef<HTMLDivElement>(null)
  const { opensLeft, ...place } = openCardPlace(ticket, spot, page.board.opensLeft(ticket))
  // The card scrolls back into view whenever one of its bars opens or closes, since the card grows or shrinks with it.
  const openPlaces = state.tiles
    .filter(tile => tile.ticket.name === ticket.name)
    .map(tile => tile.place)
    .join(' ')
  // Braces matter: newer browsers return a promise from scrollIntoView, and React would call it as the effect's cleanup.
  useEffect(() => {
    card.current?.scrollIntoView({ block: 'nearest', inline: 'nearest' })
  }, [openPlaces])
  useColumnsReachOpenCard(card)
  return (
    <div ref={card} className={opensLeft ? 'card-open grows-left' : 'card-open'} data-open-card={ticket.name} style={{ ...place, borderColor: borderColorOf(ticket), borderWidth: ticket.isActive ? ACTIVE_BORDER_WIDTH : 1 }}>
      <CardFaceView ticket={ticket} stage={stage} />
      {ticket.progressIn(stage).map(progress => (
        <TileView key={progress.fidelity.slug} ticket={ticket} stage={stage} progress={progress} hasPracticeChip opensOnHover />
      ))}
    </div>
  )
}

const borderColorOf = (ticket: TicketClient, isSelected = false): string => (ticket.isActive ? 'var(--accent)' : isSelected ? 'var(--text)' : 'var(--border)')

export function TicketCardView({ ticket, spot }: { ticket: TicketClient; spot: CardSpot }) {
  const { page, state } = useBoard()
  const stage = page.board.stageOf(ticket)
  const isSelected = page.board.selectedTicket?.address === ticket.address
  if (!stage) return null
  // Every card drags, locked or not: Active session only keeps commands to the active session's chat, and a move runs
  // nothing in a chat. An opened card closes when the drag ends.
  const isDraggable = true
  const dragStarted = (event: DragEvent) => {
    event.dataTransfer.setData('text/plain', ticket.name)
    event.dataTransfer.effectAllowed = 'move'
    page.store.change({ dragged: ticket.address })
  }
  const dragEnded = () => page.store.change(current => ({ dragged: null, openCard: current.openCard === ticket.name ? null : current.openCard }))
  return (
    <div
      className={['ticket-card', ticket.isActive ? 'is-active' : '', state.dragged === ticket.address ? 'is-dragged' : ''].filter(Boolean).join(' ')}
      data-ticket={ticket.name}
      draggable={isDraggable}
      onDragStart={dragStarted}
      onDragEnd={dragEnded}
      onClick={() => void ticket.choose()}
      style={{ borderColor: borderColorOf(ticket, isSelected), borderWidth: ticket.isActive ? ACTIVE_BORDER_WIDTH : 1 }}
    >
      {/* Chrome starts no drag on a button, and this one covers the card, so it carries the card's drag. */}
      <button className="card-hit" aria-label={`Show ${ticket.title}`} draggable={isDraggable} />
      <CardFaceView ticket={ticket} stage={stage} />
      {state.openCard === ticket.name ? <OpenCardView ticket={ticket} stage={stage} spot={spot} /> : null}
    </div>
  )
}
