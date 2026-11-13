import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { AppData } from '@cdd/harness/diagnostics/app'

import { BoardStore } from '../shared/board-store'
import { EditorAppClient } from './editor-app-client'

const PROJECT = 'C:/dev/checkout-flow'
const SERVER = { folder: 'space/kanban/app', command: ['node', '--import', 'tsx', 'packages/session-board/serve.ts'] }
// The Story UI editor as BoardFidelity.editor sends it for the Stories story-map row.
const STORY_UI: AppData = { label: 'Story UI', status: 'running', port: 8778, url: 'http://127.0.0.1:8778/story-map', server: SERVER }
const GRAPH: AppData = { label: 'Graph', status: 'running', port: 5173, url: 'http://127.0.0.1:5173/', server: SERVER }

// What Python's app.open answers for an app, as the generated client posts it.
const answering = (app: AppData, status: AppData['status']): { api: CddApi; posted: string[] } => {
  const posted: string[] = []
  const api: CddApi = {
    post: async <Result>(path: string) => {
      posted.push(path)
      return { ...app, status } as unknown as Result
    },
  }
  return { api, posted }
}

async function opened(app: AppData, status: AppData['status'], open: (client: EditorAppClient) => Promise<void>) {
  const windows: string[] = []
  const store = new BoardStore()
  const { api, posted } = answering(app, status)
  await open(new EditorAppClient(store, api, url => windows.push(url)))
  return { posted, windows, toasts: store.state.toasts.map(toast => toast.text) }
}

// The story-map row's editor widget opens the Story UI editor on the ticket's worktree, where the ticket's session is
// the open one, so the editor shows the ticket's story map.
describe('Open Story UI On Ticket Scope', () => {
  const fromRow = (client: EditorAppClient) => client.openOn(client.editorOf(STORY_UI), PROJECT)

  describe('with the Story UI editor running', () => {
    it("should open the Story UI editor's page on the ticket's worktree", async () => {
      const { posted, windows } = await opened(STORY_UI, 'running', fromRow)
      expect([posted, windows]).toEqual([['/app/Story%20UI/open'], ['http://127.0.0.1:8778/story-map?project=C%3A%2Fdev%2Fcheckout-flow']])
    })
  })

  // (S) Refactor Story UI App To Web Domain Access: the editor names the ticket's chat, whose file viewer shows a story's
  // acceptance tests.
  describe("on a ticket with a chat", () => {
    it("should name the ticket's chat in the Story UI editor's page link", async () => {
      const { windows } = await opened(STORY_UI, 'running', client => client.openOn(client.editorOf(STORY_UI), PROJECT, 'ad6c04ab-chat'))
      expect(windows).toEqual(['http://127.0.0.1:8778/story-map?project=C%3A%2Fdev%2Fcheckout-flow&chat=ad6c04ab-chat'])
    })
  })

  describe('with the Story UI editor not running', () => {
    it("should open nothing and say to open it from the chat bar's status row", async () => {
      const { windows, toasts } = await opened(STORY_UI, 'not running', fromRow)
      expect([windows, toasts]).toEqual([[], ["The Story UI app is not running: open it from the chat bar's status row, which starts it for that chat."]])
    })
  })
})

// A ticket's graph widget, or the board header, opens the Graph app on a project, so the graph shows the session open there.
describe('Filter Knowledge Graph To Ticket Scope', () => {
  const fromWidget = (client: EditorAppClient) => client.openOn(client.graph, PROJECT)

  describe('with the Graph app running', () => {
    it("should open its page on the ticket's worktree", async () => {
      const { posted, windows } = await opened(GRAPH, 'running', fromWidget)
      expect([posted, windows]).toEqual([['/app/Graph/open'], ['http://127.0.0.1:5173/?project=C%3A%2Fdev%2Fcheckout-flow']])
    })
  })

  describe('with the Graph app not running', () => {
    it("should open nothing and say to open it from the chat bar's status row", async () => {
      const { windows, toasts } = await opened(GRAPH, 'not running', fromWidget)
      expect([windows, toasts]).toEqual([[], ["The Graph app is not running: open it from the chat bar's status row, which starts it for that chat."]])
    })
  })
})
