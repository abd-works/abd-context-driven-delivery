import { describe, expect, it } from 'vitest'

import type { BoardData, ColumnData } from '@cdd/space/kanban/board'
import type { TicketData } from '@cdd/space/kanban/ticket'

import { BoardPage } from './board-page'
import type { Send } from './board-api'
import { PendingChanges, TicketMove, TicketNewParent, TicketPlacedBefore, TicketPulledOut, TicketTextEdit } from '../shared/pending-changes'

const ticket = (name: string, column: string, isDone = false, text = ''): TicketData => ({ name, title: name, text, column: { name: column }, is_done: isDone, is_stacked: false, is_pulled_out: false, is_closed: false, children: [] }) as unknown as TicketData

const stage = (name: string, inProgress: TicketData[], done: TicketData[] = []): ColumnData => ({ name, kind: 'stage', in_progress: inProgress, done })

const boardOf = (...columns: ColumnData[]): BoardData => ({ project: 'pets', practices: [], open_tickets: [], active: null, columns, fidelities: [], sends_fixes_directly: false, unsaved: null })

// Discovery holds checkout-flow and pet-visits In progress; Specification holds nothing yet.
const read = (): BoardData => boardOf(stage('Discovery', [ticket('checkout-flow', 'Discovery'), ticket('pet-visits', 'Discovery')]), stage('Specification', []))

const namesIn = (board: BoardData, column: string, list: 'in_progress' | 'done'): string[] => (board.columns.find(shown => shown.name === column)?.[list] ?? []).map(shown => shown.name)

describe('a change a person makes on the board', () => {
  describe('that moves a ticket to another stage', () => {
    const changes = (): PendingChanges => {
      const pending = new PendingChanges()
      pending.add(new TicketMove('checkout-flow', 'Specification', true))
      return pending
    }

    it('should show the ticket in that stage before the server answers', () => {
      expect(namesIn(changes().over(read()), 'Specification', 'done')).toEqual(['checkout-flow'])
    })

    it('should take the ticket out of the stage it left', () => {
      expect(namesIn(changes().over(read()), 'Discovery', 'in_progress')).toEqual(['pet-visits'])
    })

    it('should keep showing the move over a read that started before the server saved it', () => {
      const pending = changes()
      pending.over(read())
      expect(namesIn(pending.over(read()), 'Specification', 'done')).toEqual(['checkout-flow'])
    })

    it('should be dropped once a read shows it', () => {
      const pending = changes()
      pending.over(boardOf(stage('Discovery', [ticket('pet-visits', 'Discovery')]), stage('Specification', [], [ticket('checkout-flow', 'Specification', true)])))
      expect(namesIn(pending.over(read()), 'Discovery', 'in_progress')).toEqual(['checkout-flow', 'pet-visits'])
    })

    it('should be dropped once it has waited too long for a read to show it', () => {
      let now = 0
      const pending = new PendingChanges(() => now)
      pending.add(new TicketMove('checkout-flow', 'Specification', true))
      now = 60_000
      expect(namesIn(pending.over(read()), 'Specification', 'done')).toEqual([])
    })
  })

  describe('that puts a card above another in its list', () => {
    it('should show the card above the other', () => {
      const pending = new PendingChanges()
      pending.add(new TicketPlacedBefore('pet-visits', 'checkout-flow'))
      expect(namesIn(pending.over(read()), 'Discovery', 'in_progress')).toEqual(['pet-visits', 'checkout-flow'])
    })
  })

  describe("that edits a ticket's text", () => {
    it('should show the text typed', () => {
      const pending = new PendingChanges()
      pending.add(new TicketTextEdit('pet-visits', 'Book a walk'))
      const shown = pending.over(read()).columns[0].in_progress?.find(card => card.name === 'pet-visits')
      expect(shown?.text).toBe('Book a walk')
    })
  })

  describe('that gives a ticket a parent', () => {
    const given = (): BoardData => {
      const pending = new PendingChanges()
      pending.add(new TicketNewParent('pet-visits', 'checkout-flow'))
      return pending.over(read())
    }

    it("should show the ticket stacked in the parent's card", () => {
      expect(given().columns[0].in_progress?.find(card => card.name === 'checkout-flow')?.children.map(child => child.name)).toEqual(['pet-visits'])
    })

    it('should take the card out of its column', () => {
      expect(namesIn(given(), 'Discovery', 'in_progress')).toEqual(['checkout-flow'])
    })
  })

  describe('that pulls a child out of its parent', () => {
    // pet-visits stacked in checkout-flow's card.
    const parented = (): BoardData => boardOf(stage('Discovery', [{ ...ticket('checkout-flow', 'Discovery'), children: [{ ...ticket('pet-visits', 'Discovery'), is_stacked: true }] }]), stage('Specification', []))

    const pulled = (): BoardData => {
      const pending = new PendingChanges()
      pending.add(new TicketPulledOut('pet-visits'))
      return pending.over(parented())
    }

    it('should show the child as a card of its own in its column', () => {
      expect(namesIn(pulled(), 'Discovery', 'in_progress')).toEqual(['checkout-flow', 'pet-visits'])
    })

    it("should keep the child as a row in its parent's card", () => {
      expect(pulled().columns[0].in_progress?.[0]?.children.map(child => child.is_pulled_out)).toEqual([true])
    })

    describe('and then given no parent', () => {
      it('should show the child as a card of its own only', () => {
        const pending = new PendingChanges()
        pending.add(new TicketNewParent('pet-visits', null))
        const shown = pending.over(parented())
        expect([namesIn(shown, 'Discovery', 'in_progress'), shown.columns[0].in_progress?.[0]?.children]).toEqual([['checkout-flow', 'pet-visits'], []])
      })
    })
  })

  describe('that the server refuses', () => {
    // The server answers the board's read with the board as it was, and refuses every change.
    const refusing: Send = async path => (path.endsWith('/board/show') ? new Response(JSON.stringify(read())) : new Response(JSON.stringify({ error: 'checkout-flow has children' }), { status: 409 }))

    async function refused(): Promise<BoardPage> {
      const page = new BoardPage(refusing)
      await page.reader.refresh()
      await page.reader.change(new TicketMove('checkout-flow', 'Specification', false), () => page.api.post('/ticket/checkout-flow/move-to'))
      return page
    }

    it('should put the ticket back where it was', async () => {
      expect(namesIn((await refused()).store.state.board as BoardData, 'Discovery', 'in_progress')).toEqual(['checkout-flow', 'pet-visits'])
    })

    it("should show the server's refusal", async () => {
      expect((await refused()).store.state.toasts.map(toast => toast.text)).toContain('checkout-flow has children')
    })
  })
})
