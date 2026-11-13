import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardAdapter } from '@cdd/space/kanban/board'
import { BoardOnProject } from 'test-utils/board-page-support'

const TITLE = 'Sign up & pay'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

describe('Add Backlog Item', () => {
  it('should stay off with no title', async () => {
    const { page, asked } = await board.page()
    page.draft.open()
    await page.draft.add()
    expect(asked).toEqual([])
  })

  describe('with a title and text typed', () => {
    async function added() {
      const { page } = await board.page()
      page.draft.open()
      page.draft.type('title', ` ${TITLE} `)
      page.draft.type('text', 'An idea.')
      await page.draft.add()
      return page
    }

    it('should write the title and text', async () => {
      await added()
      const saved = await new BoardAdapter(board.project.cdd).show()
      expect(saved.columns.flatMap(column => column.items ?? []).find(item => item.title === TITLE)?.text).toBe('An idea.')
    })

    it('should select the item', async () => {
      expect((await added()).store.state.selected).toBe(`Backlog/${TITLE}`)
    })

    it('should say so in a toast', async () => {
      expect((await added()).store.state.toasts.at(-1)?.text).toBe(`${TITLE} added to Backlog`)
    })

    it('should close the form', async () => {
      expect((await added()).store.state.draft.isOpen).toBe(false)
    })
  })

  describe('Drop Backlog Item On Another', () => {
    async function twoItems() {
      board.write('.sessions/_backlog/checkout.md', '# Checkout\n\nPay for it.\n')
      board.write('.sessions/_backlog/gift-cards.md', '# Gift cards\n\nSell them at the till.\n')
      const { page } = await board.page()
      const named = (title: string) => page.board.backlogItems.find(item => item.title === title)!
      return { page, checkout: named('Checkout'), giftCards: named('Gift cards') }
    }

    async function backlogOrder(): Promise<string[]> {
      const saved = await new BoardAdapter(board.project.cdd).show()
      return saved.columns.flatMap(column => column.items ?? []).map(item => item.title).filter(title => ['Checkout', 'Gift cards'].includes(title))
    }

    it('should put it above near the top edge', async () => {
      const { checkout, giftCards } = await twoItems()
      expect(checkout.dropOf(giftCards, 0.1)).toBe('before')
    })

    it('should put it below near the bottom edge', async () => {
      const { checkout, giftCards } = await twoItems()
      expect(checkout.dropOf(giftCards, 0.9)).toBe('after')
    })

    it('should make it a child in the middle', async () => {
      const { checkout, giftCards } = await twoItems()
      expect(checkout.dropOf(giftCards, 0.5)).toBe('child')
    })

    it('should keep it below the other once dropped there', async () => {
      const { checkout, giftCards } = await twoItems()
      await giftCards.take(checkout, 'after')
      expect(await backlogOrder()).toEqual(['Gift cards', 'Checkout'])
    })

    describe('in the middle', () => {
      async function nested() {
        const { page, checkout, giftCards } = await twoItems()
        await checkout.take(giftCards, 'child')
        return page
      }

      it('should stack it inside the other card', async () => {
        await nested()
        const saved = await new BoardAdapter(board.project.cdd).show()
        const items = saved.columns.flatMap(column => column.items ?? []).filter(item => ['Checkout', 'Gift cards'].includes(item.title))
        expect(items.map(item => [item.title, item.children.map(child => child.title)])).toEqual([['Checkout', ['Gift cards']]])
      })

      it('should say so in a toast', async () => {
        expect((await nested()).store.state.toasts.at(-1)?.text).toBe('Gift cards is now a child of Checkout')
      })

      it('should not offer the parent as a child of its own child', async () => {
        const page = await nested()
        const parent = page.board.backlogItems.find(item => item.title === 'Checkout')!
        const child = page.board.backlogItems.find(item => item.title === 'Gift cards')!
        expect(child.canTakeAsChild(parent)).toBe(false)
      })
    })
  })

  describe('Start Backlog Item', () => {
    async function started() {
      board.write('.sessions/_backlog/sign-up-pay.md', `# ${TITLE}\n\nAn idea.\n`)
      const { page } = await board.page()
      await page.board.backlogItems.find(item => item.title === TITLE)!.start()
      return page
    }

    it('should open a ticket and select it, with the title safe in the path', async () => {
      expect((await started()).store.state.selected).toBe('Discovery/sign-up-pay')
    })

    it('should say so in a toast', async () => {
      expect((await started()).store.state.toasts.at(-1)?.text).toBe(`${TITLE} started in Discovery`)
    })
  })
})
