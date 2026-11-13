import { PROJECT_QUERY, type CddApi } from '@cdd/cdd-shared'
import { AppClientGenerated } from '@cdd/harness/diagnostics/app'

import type { BoardStore } from '../shared/board-store'

// The app the board's graph widgets open, by the label it registered under, as a tool call names it.
const GRAPH_APP = 'Graph'
const NOT_RUNNING = "The Graph app is not running: open it from the chat bar's status row, which starts it for that chat."

// The Graph app, opened in a window of its own on a project: a ticket's worktree, where that ticket's session is the open
// one, or the board's own project from the header, whose open session is the board's active ticket. Every call the app
// then makes works in that session, so it shows that session's practice trees, read from its practice roots. Python's
// App.open says where the app answers; the chat that opened it runs its server.
export class GraphAppClient {
  constructor(
    private readonly store: BoardStore,
    private readonly api: CddApi,
    private readonly openWindow: (url: string) => void = url => void window.open(url, '_blank'),
  ) {}

  async openOn(project: string): Promise<void> {
    const app = await AppClientGenerated.named(this.api, GRAPH_APP).open()
    if (!app) return
    if (app.status !== 'running') {
      this.store.toast(NOT_RUNNING, true)
      return
    }
    const page = new URL(app.url)
    page.searchParams.set(PROJECT_QUERY, project)
    this.openWindow(page.toString())
  }
}
