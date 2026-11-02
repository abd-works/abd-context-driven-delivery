import { useEffect, useRef, useState } from 'react'
import type { MouseEvent } from 'react'

import type { Column } from './board'
import { ageOf, practiceOf, SEGMENT_LIGHT } from './board-brand'
import { useBoard } from './board-context'
import { ActionBarView } from './action-bar-view'
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

function SegmentsView({ ticket, stage, onSkill }: { ticket: TicketClient; stage: Column; onSkill: (skill: string) => void }) {
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
          <button key={slug} className="segment-hit" title={skill} aria-label={`${skill}: ${label}`} aria-expanded={isOpen} onClick={withoutSelecting(() => page.tiles.openSegment(ticket, stage, slug))} onMouseEnter={enter} onMouseLeave={leave} onFocus={enter} onBlur={leave}>
            <span className="segment" style={{ background, opacity: SEGMENT_LIGHT[key] }} />
          </button>
        )
      })}
    </div>
  )
}

function FileLinksView({ ticket, slugs }: { ticket: TicketClient; slugs: string[] }) {
  const { page } = useBoard()
  return (
    <div className="card-files">
      {['list', 'folder', 'files'].map(mode => (
        <button key={mode} className="extra-action" onClick={withoutSelecting(() => page.panels.openFiles(ticket.name, slugs, mode))}>
          {mode}
        </button>
      ))}
    </div>
  )
}

function CardMarkView({ ticket, stage }: { ticket: TicketClient; stage: Column }) {
  const { page, state } = useBoard()
  const isOpen = state.openCard === ticket.name
  return (
    <button className="expand-mark card-mark" aria-label={`Actions for ${ticket.title}`} aria-expanded={isOpen} onClick={withoutSelecting(() => page.tiles.toggleCard(ticket, stage))}>
      {isOpen ? '▴' : '▾'}
    </button>
  )
}

function CardFaceView({ ticket, stage }: { ticket: TicketClient; stage: Column }) {
  const { page, state } = useBoard()
  const [skill, setSkill] = useState('')
  return (
    <>
      <CardMarkView ticket={ticket} stage={stage} />
      <div className="ticket-title">{ticket.title}</div>
      <div className="ticket-meta">{ageOf(state.now, ticket.last_activity)}</div>
      <SegmentsView ticket={ticket} stage={stage} onSkill={setSkill} />
      {skill ? <div className="card-skill">{skill}</div> : null}
      {ticket.violations.length ? (
        <button className="violations-link card-violations" onClick={withoutSelecting(() => page.panels.openReport(ticket.name, ''))}>
          violations
        </button>
      ) : null}
      <FileLinksView ticket={ticket} slugs={ticket.enabledSlugs(stage)} />
    </>
  )
}

function MoveRowView({ ticket }: { ticket: TicketClient }) {
  const { page } = useBoard()
  return (
    <div className="card-moves">
      <button className="action card-move" title={ticket.backLabel} aria-label={ticket.backLabel} disabled={ticket.isLocked} onClick={withoutSelecting(() => ticket.movePrevious())}>
        ←
      </button>
      <button className="action card-activate" disabled={ticket.isClosed} onClick={withoutSelecting(() => page.activation.start(ticket, ticket.isActive))}>
        {ticket.isActive ? 'Close' : 'Activate'}
      </button>
      <button className="action card-move" aria-label={`Move ${ticket.title} to the next column`} disabled={ticket.isLocked || !ticket.can_move_next} onClick={withoutSelecting(() => ticket.moveNext())}>
        →
      </button>
    </div>
  )
}

// An open card shows the same tiles as the details, so a ticket can be worked from either place.
function OpenCardView({ ticket, stage, spot }: { ticket: TicketClient; stage: Column; spot: CardSpot }) {
  const { state } = useBoard()
  const card = useRef<HTMLDivElement>(null)
  const { opensLeft, ...place } = openCardPlace(ticket, spot)
  const hasBar = state.cardMenu?.ticket === ticket.name
  useEffect(() => card.current?.scrollIntoView({ block: 'nearest', inline: 'nearest' }), [hasBar])
  return (
    <div ref={card} className={opensLeft ? 'card-open grows-left' : 'card-open'} data-open-card={ticket.name} style={{ ...place, borderColor: borderColorOf(ticket), borderWidth: ticket.isActive ? ACTIVE_BORDER_WIDTH : 1 }}>
      <CardFaceView ticket={ticket} stage={stage} />
      {state.cardMenu?.ticket === ticket.name ? <ActionBarView ticket={ticket} stage={stage} tile={state.cardMenu} hasFileLinks={false} /> : null}
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
  const isSelected = page.board.selectedTicket?.name === ticket.name && page.board.selectedTicket.column === ticket.column
  if (!stage) return null
  return (
    <div className="ticket-card" data-ticket={ticket.name} onClick={() => ticket.select()} style={{ borderColor: borderColorOf(ticket, isSelected), borderWidth: ticket.isActive ? ACTIVE_BORDER_WIDTH : 1 }}>
      <button className="card-hit" aria-label={`Show ${ticket.title}`} />
      <CardFaceView ticket={ticket} stage={stage} />
      {state.openCard === ticket.name ? <OpenCardView ticket={ticket} stage={stage} spot={spot} /> : null}
      <MoveRowView ticket={ticket} />
    </div>
  )
}
