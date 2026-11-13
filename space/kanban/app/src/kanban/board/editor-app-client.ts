import { PROJECT_QUERY, type CddApi } from '@cdd/cdd-shared'
import { AppClientGenerated, type AppData } from '@cdd/harness/diagnostics/app'

import type { BoardStore } from '../shared/board-store'

// The apps' identities, the labels they registered under, as their generated clients name them.
const GRAPH_APP = 'Graph'
const KANBAN_APP = 'Kanban'

// Opens any App in a window of its own on a project: a ticket's worktree, where that ticket's session is the open one, or
// the board's own project from the header, whose open session is the board's active ticket. Every call the app then
// makes works in that session. The Story UI editor opens from the Stories story-map row (Python's BoardFidelity.editor
// names it), the Graph app from the header and from each ticket's graph widget. Python's App.open readies the app and says
// where it answers; the chat that opened it runs its server.
export class EditorAppClient {
  readonly graph: AppClientGenerated
  // The board itself, which Update installs again, rebuilding the page this board loads.
  readonly kanban: AppClientGenerated

  constructor(
    private readonly store: BoardStore,
    private readonly api: CddApi,
    private readonly openWindow: (url: string) => void = url => void window.open(url, '_blank'),
  ) {
    this.graph = AppClientGenerated.named(api, GRAPH_APP)
    this.kanban = AppClientGenerated.named(api, KANBAN_APP)
  }

  // The editor a practice row names, as the board read sent it.
  editorOf(editor: AppData): AppClientGenerated {
    return new AppClientGenerated(this.api, editor)
  }

  async openOn(app: AppClientGenerated, project: string): Promise<void> {
    const opened = await app.open()
    if (!opened) return
    if (opened.status !== 'running') {
      this.store.toast(`The ${opened.label} app is ${opened.status}: open it from the chat bar's status row, which starts it for that chat.`, true)
      return
    }
    const page = new URL(opened.url)
    page.searchParams.set(PROJECT_QUERY, project)
    this.openWindow(page.toString())
  }
}
