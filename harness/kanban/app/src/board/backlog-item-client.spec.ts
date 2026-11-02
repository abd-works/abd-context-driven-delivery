import { describe, expect, it } from 'vitest'

import type { BacklogItem } from './board'
import { boardJson, discovery, pageOn, ticketJson } from './spec-support'

const ITEM: BacklogItem = { title: 'Sign up & pay', text: 'An idea.', path: '.sessions/_backlog/sign-up.md', last_activity: '' }

describe('Add Backlog Item', () => {
  it('should stay off with no title', async () => {
    const { page, server } = pageOn(boardJson([discovery()]))
    page.draft.open()
    await page.draft.add()
    expect(server.requests).toEqual([])
  })

  it('should write the title and text, select the item, and say so', async () => {
    const { page, server } = pageOn(boardJson([discovery()], null, [ITEM]))
    server.answer('POST /api/backlog', ITEM)
    page.draft.open()
    page.draft.type('title', ' Sign up & pay ')
    page.draft.type('text', 'An idea.')
    await page.draft.add()
    expect(server.posted('/api/backlog')[0]?.body).toEqual({ title: 'Sign up & pay', text: 'An idea.' })
    expect(page.store.state.selected).toBe('Backlog/Sign up & pay')
    expect(page.store.state.toasts.at(-1)?.text).toBe('Sign up & pay added to Backlog')
    expect(page.store.state.draft.isOpen).toBe(false)
  })

  describe('Start Backlog Item', () => {
    it('should open a ticket and select it, with the title safe in the path', async () => {
      const { page, server } = pageOn(boardJson([discovery()], null, [ITEM]))
      server.answer('POST /api/backlog/Sign%20up%20%26%20pay/start', ticketJson('sign-up-pay'))
      await page.item(ITEM).start()
      expect(page.store.state.selected).toBe('Discovery/sign-up-pay')
      expect(page.store.state.toasts.at(-1)?.text).toBe('Sign up & pay started in Discovery')
    })
  })
})
