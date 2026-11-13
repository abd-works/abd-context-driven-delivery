import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject } from 'test-utils/board-page-support'

// billing-report is a ticket the board shows; main is the default session, no ticket of its own.
const TICKET = 'billing-report'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

describe('A ticket a person clicks', () => {
  that('has its own chat open', () => {
    it('should show its chat at the top of the board', async () => {
      const { page } = await board.page()
      await board.chat('chat-ticket', TICKET).checkIn()
      await page.chat.refresh()
      page.cards.open(page.board.tickets.find(ticket => ticket.name === TICKET)!)
      expect(page.store.state.targetChat).toBe('chat-ticket')
    })
  })

  that('has no chat open of its own while main has one', () => {
    it('should show main’s chat at the top of the board', async () => {
      const { page } = await board.page()
      await board.chat('chat-main', 'main').checkIn()
      await page.chat.refresh()
      page.cards.open(page.board.tickets.find(ticket => ticket.name === TICKET)!)
      expect(page.store.state.targetChat).toBe('chat-main')
    })
  })

  that('has no chat open while neither has main', () => {
    it('should show no chat at the top of the board, not the one picked before', async () => {
      const { page } = await board.page()
      await board.chat('chat-other').checkIn()
      await page.chat.refresh()
      page.chat.choose('chat-other')
      page.cards.open(page.board.tickets.find(ticket => ticket.name === TICKET)!)
      expect(page.store.state.targetChat).toBeNull()
    })
  })
})

describe('The board', () => {
  it('should count no card for main, the default session', async () => {
    const { page } = await board.page()
    const holdingMain = page.board.shownColumns.find(column => column.everyTicket.some(ticket => ticket.isMain))!
    expect(holdingMain.count).toBe(holdingMain.everyTicket.length - 1)
  })
})

function that(state: string, body: () => void): void {
  describe(`that ${state}`, body)
}
