import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardAdapter } from '@cdd/harness/kanban/board'
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
