import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject, ticketOn } from 'test-utils/board-page-support'

import type { BoardPage } from '../board/board-page'
import { TICKET_ROOT } from './root-choice-client'

// checkout-flow is the fixture's active ticket, working on the whole repository.
const TICKET = 'checkout-flow'
const ITEM = 'Gift cards'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => {
  board.reset()
  board.write('src/visits/visit.ts', '')
  board.write('src/billing/bill.ts', '')
})

afterAll(() => board.close())

const browsing = (page: BoardPage) => page.store.state.rootChoice?.browsing

async function openedFor(ticket: string) {
  const { page } = await board.page()
  page.roots.openFor(ticketOn(page, ticket))
  return page
}

describe('Choose Session Root', () => {
  describe('with the roots of a ticket open', () => {
    it("should show the ticket's practices with their roots", async () => {
      const page = await openedFor(TICKET)
      expect(Object.keys(page.roots.ticket!.session.practices)).toContain('stories')
    })

    describe('that a person browses into a folder for the session workpath', () => {
      async function browsed() {
        const page = await openedFor(TICKET)
        await page.roots.browse(TICKET_ROOT, 'src')
        return page
      }

      it('should list the folders inside it', async () => {
        expect(browsing(await browsed())?.folders).toEqual(['src/billing', 'src/visits'])
      })

      it('should go back up to the top of the repository', async () => {
        const page = await browsed()
        await page.roots.up()
        expect(browsing(page)?.path).toBe('')
      })

      describe('and uses it', () => {
        async function used() {
          const page = await browsed()
          await page.roots.browse(TICKET_ROOT, 'src/visits')
          await page.roots.use()
          return page
        }

        it("should make it the ticket's workpath", async () => {
          expect(ticketOn(await used(), TICKET).session.workpath).toBe('src/visits')
        })

        it('should go back to the list of roots', async () => {
          expect(browsing(await used())).toBeNull()
        })
      })
    })

    describe("that a person chooses a folder for one practice's root", () => {
      async function chosen() {
        const page = await openedFor(TICKET)
        await page.roots.browse('stories', 'src/billing')
        await page.roots.use()
        return page
      }

      it("should show it as that practice's chosen root", async () => {
        expect(ticketOn(await chosen(), TICKET).session.practices.stories).toMatchObject({ root: 'src/billing', is_root_chosen: true })
      })

      describe('and then goes back to its default', () => {
        it('should show the practice on its default root', async () => {
          const page = await chosen()
          await page.roots.useDefault('stories')
          expect(ticketOn(page, TICKET).session.practices.stories?.is_root_chosen).toBe(false)
        })
      })
    })
  })

  describe('with a backlog item a person has asked to start', () => {
    async function asked() {
      board.write('.sessions/_backlog/gift-cards.md', `# ${ITEM}\n`)
      const { page } = await board.page()
      await page.roots.openToStart(page.board.backlogItems.find(item => item.title === ITEM)!)
      return page
    }

    it('should browse the top of the repository for its workpath before it starts', async () => {
      expect(browsing(await asked())?.path).toBe('')
    })

    it('should not start it yet', async () => {
      expect((await asked()).board.backlogItems.map(item => item.title)).toContain(ITEM)
    })

    describe('that a person has started in a folder', () => {
      async function started() {
        const page = await asked()
        await page.roots.browse(TICKET_ROOT, 'src/visits')
        await page.roots.use()
        return page
      }

      it('should open its ticket with that folder as its workpath', async () => {
        expect(ticketOn(await started(), 'gift-cards').session.workpath).toBe('src/visits')
      })

      it("should stay open on the new ticket's roots, so its practices' roots can be set", async () => {
        expect((await started()).store.state.rootChoice?.ticket?.name).toBe('gift-cards')
      })
    })
  })
})
