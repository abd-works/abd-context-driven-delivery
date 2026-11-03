import type { BoardData, ColumnData } from '@cdd/harness/kanban/board'
import { BoardPage } from '@src/kanban/board/board-page'
import type { ColumnClient } from '@src/kanban/board/column-client'
import type { Chat } from '@src/kanban/chat/chat'

import { boardJson } from './board-examples'

const OK = 200

type Answer = { status: number; body: unknown }
type Request = { method: string; path: string; body: Record<string, unknown> | undefined; headers: Record<string, string> }

// The page's server as a table of answers, keyed by method and path, recording what the page asked. An answer keyed by
// method, path, and the JSON it was sent wins, because one route reads different things for different arguments.
export class FakeServer {
  readonly requests: Request[] = []
  readonly answers = new Map<string, Answer>()

  answer(route: string, body: unknown, status: number = OK): this {
    this.answers.set(route, { status, body })
    return this
  }

  posted(path: string): Request[] {
    return this.requests.filter(request => request.method === 'POST' && request.path === path)
  }

  readonly send = (path: string, init?: RequestInit): Promise<Response> => {
    const method = init?.method ?? 'GET'
    const body = init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : undefined
    this.requests.push({ method, path, body, headers: (init?.headers ?? {}) as Record<string, string> })
    const found = this.answers.get(`${method} ${path} ${JSON.stringify(body)}`) ??
      this.answers.get(`${method} ${path}`) ?? { status: 404, body: { error: `no answer for ${method} ${path}` } }
    return Promise.resolve(new Response(JSON.stringify(found.body), { status: found.status }))
  }
}

export function pageOn(board: BoardData | null): { page: BoardPage; server: FakeServer } {
  const server = new FakeServer()
  if (board) server.answer('POST /api/board/show', board)
  const page = new BoardPage(server.send)
  page.store.change({ board })
  return { page, server }
}

export const stageOn = (column: ColumnData): ColumnClient => pageOn(boardJson([column])).page.board.stages[0]!

export function withChat(page: BoardPage, server: FakeServer, chat: Chat = { id: 'chat-1', name: 'Chat one', isBusy: false }): void {
  page.store.change({ chats: [chat], targetChat: chat.id })
  server.answer(`POST /api/chats/${chat.id}/commands`, { ok: true })
}
