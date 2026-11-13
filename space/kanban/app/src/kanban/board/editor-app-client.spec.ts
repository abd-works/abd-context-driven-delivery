import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { AppData } from '@cdd/harness/diagnostics/app'

import { BoardStore } from '../shared/board-store'
import { EditorAppClient } from './editor-app-client'

// The Story UI editor as FidelityProgress.editor sends it on the Stories story-map row.
const STORY_UI: AppData = {
  label: 'Story UI',
  status: 'running',
  port: 8778,
  url: 'http://127.0.0.1:8778/story-map',
  server: { folder: 'space/kanban/app', command: ['node', '--import', 'tsx', 'packages/session-board/serve.ts'] },
}

// What Python's app.open answers for the Story UI editor, as the generated client posts it.
const answering = (status: AppData['status']): { api: CddApi; posted: string[] } => {
  const posted: string[] = []
  const api: CddApi = {
    post: async <Result>(path: string) => {
      posted.push(path)
      return { ...STORY_UI, status } as unknown as Result
    },
  }
  return { api, posted }
}

// The story-map row's editor widget opens the Story UI editor on the ticket's worktree, where the ticket's session is
// the open one, so the editor shows the ticket's story map.
describe('Open Story UI On Ticket Scope', () => {
  describe('with the Story UI editor running', () => {
    it("should open the Story UI editor's page on the ticket's worktree", async () => {
      const opened: string[] = []
      const { api, posted } = answering('running')
      await new EditorAppClient(new BoardStore(), api, url => opened.push(url)).openOn(STORY_UI, 'C:/dev/checkout-flow')
      expect([posted, opened]).toEqual([['/app/Story%20UI/open'], ['http://127.0.0.1:8778/story-map?project=C%3A%2Fdev%2Fcheckout-flow']])
    })
  })

  describe('with the Story UI editor not running', () => {
    it("should open nothing and say to open it from the chat bar's status row", async () => {
      const opened: string[] = []
      const store = new BoardStore()
      await new EditorAppClient(store, answering('not running').api, url => opened.push(url)).openOn(STORY_UI, 'C:/dev/checkout-flow')
      expect([opened, store.state.toasts.map(toast => toast.text)]).toEqual([[], ["The Story UI is not running: open it from the chat bar's status row, which starts it for that chat."]])
    })
  })
})
