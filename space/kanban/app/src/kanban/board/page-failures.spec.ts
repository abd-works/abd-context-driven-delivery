import { describe, expect, it } from 'vitest'

import { BoardApi, type Send } from './board-api'
import { BoardPage } from './board-page'
import { PageFailures } from './page-failures'
import { BoardStore } from '../shared/board-store'

const CHAT = 'ad6c04ab-chat'
const CHAT_SEND = `/api/chat/${CHAT}/send`
const REFUSED = 'checkout-flow has children'

type Posted = { path: string; body: Record<string, unknown> }

// The board's server as the page reaches it: the opening chat takes every message, and every other call is refused.
function serverRefusing(posted: Posted[]): Send {
  return async (path, init) => {
    posted.push({ path, body: init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : {} })
    if (path === CHAT_SEND) return Response.json({ id: CHAT, name: 'release-2', is_busy: false, folder: '' })
    return Response.json({ error: REFUSED }, { status: 409 })
  }
}

const failuresSent = (posted: Posted[]) => posted.filter(post => post.path === CHAT_SEND && post.body.kind === 'failure').map(post => JSON.parse(String(post.body.text)))

// Every failure on the board page goes to the chat that opened it, as the Files app sends its own.
describe('Send A Board Failure To The Opening Chat', () => {
  describe('with a page a chat opened', () => {
    it('should send a refused call and where it happened to that chat', async () => {
      const posted: Posted[] = []
      const store = new BoardStore()
      const send = serverRefusing(posted)
      await new BoardApi(store, new PageFailures(store, send, CHAT), send).post('/ticket/checkout-flow/remove')
      await new Promise(done => setTimeout(done))
      expect(failuresSent(posted)).toEqual([{ failure: REFUSED, context: 'Calling /ticket/checkout-flow/remove from the Kanban board' }])
    })

    it('should show the failure on the page', async () => {
      const store = new BoardStore()
      const send = serverRefusing([])
      await new BoardApi(store, new PageFailures(store, send, CHAT), send).post('/ticket/checkout-flow/remove')
      expect(store.state.toasts.map(toast => toast.text)).toEqual([REFUSED])
    })

    describe("that the board's read every two seconds meets again", () => {
      it('should send the failure to the chat once', async () => {
        const posted: Posted[] = []
        const page = new BoardPage(serverRefusing(posted), CHAT)
        await page.reader.refresh()
        await page.reader.refresh()
        await new Promise(done => setTimeout(done))
        expect(failuresSent(posted)).toHaveLength(1)
      })
    })
  })

  describe('with a page no chat opened', () => {
    it('should only show the failure on the page', async () => {
      const posted: Posted[] = []
      const store = new BoardStore()
      const send = serverRefusing(posted)
      await new BoardApi(store, new PageFailures(store, send, ''), send).post('/ticket/checkout-flow/remove')
      expect([failuresSent(posted), store.state.toasts.map(toast => toast.text)]).toEqual([[], [REFUSED]])
    })
  })
})
