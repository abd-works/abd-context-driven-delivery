import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject } from 'test-utils/board-page-support'

import type { FilesPanel } from '../shared/board-store'

// checkout-flow is the active ticket, with a story map.
const TICKET = 'checkout-flow'
const SLUG = 'stories-story-map'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

const filesPanelOf = (panels: { kind: string }[]): FilesPanel | undefined => panels.find(shown => shown.kind === 'files') as FilesPanel | undefined

describe('Linked Files', () => {
  with_link('naming a ticket and its fidelity', () => {
    it("should open the files panel with that fidelity's practice turned on", async () => {
      const { page } = board.unreadPage()
      await page.openLinkedFiles(`?files=${TICKET}&fidelity=${SLUG}`)
      expect(filesPanelOf(page.store.state.panels)?.practicesOn).toEqual(['stories'])
    })
  })

  with_link('naming a fidelity the ticket does not have', () => {
    it('should open no panel', async () => {
      const { page } = await board.page()
      await page.openLinkedFiles(`?files=${TICKET}&fidelity=no-such-fidelity`)
      expect(filesPanelOf(page.store.state.panels)).toBeUndefined()
    })
  })

  with_link('naming nothing', () => {
    it('should open no panel', async () => {
      const { page } = await board.page()
      await page.openLinkedFiles('')
      expect(page.store.state.panels).toEqual([])
    })
  })

  with_link("naming a ticket's session folder", () => {
    it("should open the files panel on that session's folder", async () => {
      const { page } = board.unreadPage()
      await page.openLinkedSessionFolder(`?session-folder=${TICKET}`)
      expect(filesPanelOf(page.store.state.panels)?.source).toBe('session')
    })
  })

  with_link('naming a session folder of no ticket', () => {
    it('should open no panel', async () => {
      const { page } = await board.page()
      await page.openLinkedSessionFolder('?session-folder=no-such-ticket')
      expect(filesPanelOf(page.store.state.panels)).toBeUndefined()
    })
  })
})

function with_link(state: string, body: () => void): void {
  describe(`with a link ${state}`, body)
}
