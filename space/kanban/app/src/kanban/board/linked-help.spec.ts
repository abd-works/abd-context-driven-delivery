import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject } from 'test-utils/board-page-support'

import type { HelpPanel } from '../shared/board-store'

// checkout-flow is the active ticket, with a story map.
const TICKET = 'checkout-flow'
const SLUG = 'stories-story-map'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

describe('Linked Help', () => {
  with_link('naming a ticket and its fidelity', () => {
    it('should open that fidelity help panel', async () => {
      const { page } = board.unreadPage()
      await page.openLinkedHelp(`?help=${TICKET}&fidelity=${SLUG}`)
      const panel = page.store.state.panels.find(shown => shown.kind === 'help') as HelpPanel
      expect(panel.help.fidelity?.slug).toBe(SLUG)
    })
  })

  with_link('naming a fidelity the ticket does not have', () => {
    it('should open no panel', async () => {
      const { page } = await board.page()
      await page.openLinkedHelp(`?help=${TICKET}&fidelity=no-such-fidelity`)
      expect(page.store.state.panels.some(shown => shown.kind === 'help')).toBe(false)
    })
  })

  with_link('naming nothing', () => {
    it('should open no panel', async () => {
      const { page } = await board.page()
      await page.openLinkedHelp('')
      expect(page.store.state.panels).toEqual([])
    })
  })
})

function with_link(state: string, body: () => void): void {
  describe(`with a link ${state}`, body)
}
