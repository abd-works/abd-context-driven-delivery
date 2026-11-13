import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { AppData } from '@cdd/harness/diagnostics/app'

import { BoardStore } from '../shared/board-store'
import { GraphAppClient } from './graph-app-client'

// What Python's app.open answers for the Graph app, as the generated client posts it.
const answering = (status: AppData['status']): { api: CddApi; posted: string[] } => {
  const posted: string[] = []
  const api: CddApi = {
    post: async <Result>(path: string) => {
      posted.push(path)
      return { label: 'Graph', status, port: status === 'running' ? 5173 : null, url: 'http://127.0.0.1:5173/' } as unknown as Result
    },
  }
  return { api, posted }
}

// A ticket's graph widget, or the board header, opens the Graph app on a project, so the graph shows the session open there.
describe('Filter Knowledge Graph To Ticket Scope', () => {
  describe('with the Graph app running', () => {
    it("should open its page on the ticket's worktree", async () => {
      const opened: string[] = []
      const { api, posted } = answering('running')
      await new GraphAppClient(new BoardStore(), api, url => opened.push(url)).openOn('C:/dev/checkout-flow')
      expect([posted, opened]).toEqual([['/app/Graph/open'], ['http://127.0.0.1:5173/?project=C%3A%2Fdev%2Fcheckout-flow']])
    })
  })

  describe('with the Graph app not running', () => {
    it("should open nothing and say to open it from the chat bar's status row", async () => {
      const opened: string[] = []
      const store = new BoardStore()
      await new GraphAppClient(store, answering('not running').api, url => opened.push(url)).openOn('C:/dev/checkout-flow')
      expect([opened, store.state.toasts.map(toast => toast.text)]).toEqual([[], ["The Graph app is not running: open it from the chat bar's status row, which starts it for that chat."]])
    })
  })
})
