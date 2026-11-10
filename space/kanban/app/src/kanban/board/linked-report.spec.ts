import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject } from 'test-utils/board-page-support'

import type { ReportPanel } from '../shared/board-store'

// checkout-flow is the active ticket: its story map was validated with one rule broken.
const TICKET = 'checkout-flow'
const SLUG = 'stories-story-map'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

describe('Linked Report', () => {
  with_link('naming a ticket and its fidelity', () => {
    it('should open that fidelity report panel', async () => {
      const { page } = board.unreadPage()
      await page.openLinkedReport(`?report=${TICKET}&fidelity=${SLUG}`)
      const panel = page.store.state.panels.find(shown => shown.kind === 'report') as ReportPanel
      expect([panel.ticket.name, panel.progress?.fidelity.slug]).toEqual([TICKET, SLUG])
    })
  })

  with_link('naming a fidelity the ticket does not have', () => {
    it('should open no panel', async () => {
      const { page } = await board.page()
      await page.openLinkedReport(`?report=${TICKET}&fidelity=no-such-fidelity`)
      expect(page.store.state.panels.some(shown => shown.kind === 'report')).toBe(false)
    })
  })

  with_link('naming nothing', () => {
    it('should open no panel', async () => {
      const { page } = await board.page()
      await page.openLinkedReport('')
      expect(page.store.state.panels).toEqual([])
    })
  })
})

function with_link(state: string, body: () => void): void {
  describe(`with a link ${state}`, body)
}
