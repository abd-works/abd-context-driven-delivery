import type { BacklogItem, BoardData, Column, Ticket } from './board'
import { BoardPage } from './board-page'

export const DISCOVERY_SLUGS = ['stories-story_map', 'ddd-bounded_context']

export const ticketJson = (name: string, change: Partial<Ticket> = {}): Ticket => ({
  name,
  title: name,
  scope: 'feature',
  parent: '',
  column: 'Discovery',
  is_done: false,
  can_move_next: true,
  next: 'stories-story_map',
  next_action: 'generate',
  last_activity: '2026-11-01T10:00:00Z',
  handoff: '',
  reports: {},
  violation_counts: {},
  practices: { stories: true, ddd: true, ux: true, clean_engineering: true, bdd: true },
  progress: { 'stories-story_map': 'not_started', 'ddd-bounded_context': 'not_started' },
  actions: {},
  allowed_actions: { 'stories-story_map': ['generate'], 'ddd-bounded_context': ['generate'] },
  ...change,
})

export const discovery = (inProgress: Ticket[] = [], done: Ticket[] = []): Column => ({
  name: 'Discovery',
  work_required: DISCOVERY_SLUGS,
  formats: { 'stories-story_map': ['markdown', 'drawio'], 'ddd-bounded_context': ['markdown'] },
  default_formats: { 'stories-story_map': 'markdown', 'ddd-bounded_context': 'markdown' },
  wip_limit: 3,
  is_over_limit: false,
  in_progress: inProgress,
  done,
})

export const boardJson = (columns: Column[], active: string | null = null, items: BacklogItem[] = []): BoardData => ({
  project: 'pet-clinic',
  active,
  columns: [{ name: 'Backlog', items }, ...columns, { name: 'Complete', tickets: [] }],
})

type Answer = { status: number; body: unknown }
type Request = { method: string; path: string; body: Record<string, unknown> | undefined; headers: Record<string, string> }

// The page's server as a table of answers, keyed by method and path, recording what the page asked.
export class FakeServer {
  readonly requests: Request[] = []
  readonly answers = new Map<string, Answer>()

  answer(route: string, body: unknown, status = 200): this {
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
    const found = this.answers.get(`${method} ${path}`) ?? { status: 404, body: { error: `no answer for ${method} ${path}` } }
    return Promise.resolve(new Response(JSON.stringify(found.body), { status: found.status }))
  }
}

export function pageOn(board: BoardData | null): { page: BoardPage; server: FakeServer } {
  const server = new FakeServer()
  if (board) server.answer('GET /api/board', board)
  const page = new BoardPage(server.send)
  page.store.change({ board })
  return { page, server }
}

export function withChat(page: BoardPage, server: FakeServer, id = 'chat-1', isBusy = false): void {
  page.store.change({ chats: [{ id, isBusy }], targetChat: id })
  server.answer(`POST /api/chats/${id}/commands`, { ok: true })
}
