import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject } from 'test-utils/board-page-support'

// checkout-flow is the active ticket; billing-report is another ticket the board shows.
const OTHER = 'billing-report'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

describe('Linked Ticket', () => {
  with_link('naming a ticket the board shows', () => {
    it('should select that ticket', async () => {
      const { page } = board.unreadPage()
      await page.openLinkedTicket(`?ticket=${OTHER}`)
      expect(page.board.selectedTicket?.name).toBe(OTHER)
    })
  })

  with_link('naming a ticket the board does not show', () => {
    it('should select nothing', async () => {
      const { page } = await board.page()
      await page.openLinkedTicket('?ticket=no-such-ticket')
      expect(page.store.state.selected).toBeNull()
    })
  })

  with_link('naming nothing', () => {
    it('should select nothing', async () => {
      const { page } = await board.page()
      await page.openLinkedTicket('')
      expect(page.store.state.selected).toBeNull()
    })
  })
})

function with_link(state: string, body: () => void): void {
  describe(`with a link ${state}`, body)
}
