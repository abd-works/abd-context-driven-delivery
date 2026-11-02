import { describe, expect, it } from 'vitest'

import type { BacklogItemData } from '@cdd/harness/kanban/backlog-item'
import { boardJson, discovery, ticketJson } from 'test-utils/board-examples'
import { pageOn } from 'test-utils/board-page-support'

const ITEM: BacklogItemData = { title: 'Sign up & pay', text: 'An idea.', path: '.sessions/_backlog/sign-up.md', last_activity: '' }

describe('Add Backlog Item', () => {
  it('should stay off with no title', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    page.draft.open()
    await page.draft.add()
    expect(server.requests).toEqual([])
  })

  describe('with a title and text typed', () => {
    async function added() {
      const { page, server } = pageOn(boardJson([discovery()], null, [ITEM]))
      server.answer('POST /api/backlog', ITEM)
      page.draft.open()
      page.draft.type('title', ' Sign up & pay ')
      page.draft.type('text', 'An idea.')
      await page.draft.add()
      return { page, server }
    }

    it('should write the title and text', async () => {
      const { server } = await added()
      expect(server.posted('/api/backlog')[0]?.body).toEqual({ title: 'Sign up & pay', text: 'An idea.' })
    })

    it('should select the item', async () => {
      const { page } = await added()
      expect(page.store.state.selected).toBe('Backlog/Sign up & pay')
    })

    it('should say so in a toast', async () => {
      const { page } = await added()
      expect(page.store.state.toasts.at(-1)?.text).toBe('Sign up & pay added to Backlog')
    })

    it('should close the form', async () => {
      const { page } = await added()
      expect(page.store.state.draft.isOpen).toBe(false)
    })
  })

  describe('Start Backlog Item', () => {
    async function started() {
      const { page, server } = pageOn(boardJson([discovery()], null, [ITEM]))
      server.answer('POST /api/backlog/Sign%20up%20%26%20pay/start', ticketJson('sign-up-pay'))
      await page.item(ITEM).start()
      return page
    }

    it('should open a ticket and select it, with the title safe in the path', async () => {
      expect((await started()).store.state.selected).toBe('Discovery/sign-up-pay')
    })

    it('should say so in a toast', async () => {
      expect((await started()).store.state.toasts.at(-1)?.text).toBe('Sign up & pay started in Discovery')
    })
  })
})
