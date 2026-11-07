import { createElement } from 'react'
import { renderToString } from 'react-dom/server'
import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { TicketClientGenerated } from '@cdd/space/kanban/ticket'
import { TicketViewGenerated } from '@cdd/space/kanban/ticket-views'
import { BoardOnProject, ticketOn } from 'test-utils/board-page-support'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

// A generated client of a ticket as the board read it, posting through the real routes.
async function generatedTicket(name: string): Promise<TicketClientGenerated> {
  const { page } = await board.page()
  return new TicketClientGenerated(board.board.api, ticketOn(page, name).toJSON())
}

const drawn = (client: TicketClientGenerated, fields = {}): string => renderToString(createElement(TicketViewGenerated, { client, fields }))

describe('a generated ticket view', () => {
  it('should show a field no operation changes as read-only', async () => {
    expect(drawn(await generatedTicket('billing-report'))).toContain('<span class="cdd-field-value">Discovery</span>')
  })

  it('should offer an operation with no arguments as a button', async () => {
    expect(drawn(await generatedTicket('billing-report'))).toContain('>Move next</button>')
  })

  it('should give an operation with arguments a form for them', async () => {
    expect(drawn(await generatedTicket('billing-report'))).toContain('Stage')
  })

  describe('with a field the page draws itself', () => {
    it('should draw the page’s own field in its place', async () => {
      expect(drawn(await generatedTicket('billing-report'), { title: () => createElement('h1', null, 'Billing report, the page’s way') })).toContain('<h1>Billing report, the page’s way</h1>')
    })
  })
})

describe('a generated ticket client', () => {
  describe('that an operation has answered with new state', () => {
    it('should tell what is drawing it to draw again', async () => {
      const ticket = await generatedTicket('move-me')
      let draws = 0
      ticket.onChanged(() => draws++)
      await ticket.moveNext()
      expect(draws).toBe(1)
    })
  })

  describe('that the page has stopped listening to', () => {
    it('should not tell it again', async () => {
      const ticket = await generatedTicket('move-me')
      let draws = 0
      const stop = ticket.onChanged(() => draws++)
      stop()
      await ticket.moveNext()
      expect(draws).toBe(0)
    })
  })
})
