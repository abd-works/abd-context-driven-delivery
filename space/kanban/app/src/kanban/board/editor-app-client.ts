import { PROJECT_QUERY, type CddApi } from '@cdd/cdd-shared'
import { AppClientGenerated, type AppData } from '@cdd/harness/diagnostics/app'

import type { BoardStore } from '../shared/board-store'

// The editor a practice row's widget opens, in a window of its own, on a ticket's worktree, where that ticket's session
// is the open one: the Story UI editor on the Stories story-map row, which then shows the ticket's story map. Python's
// FidelityProgress.editor names the app; App.open readies it (installs it while it is not installed) and says where it
// answers. The Story UI editor answers on this board's own server, so it runs whenever the board does.
export class EditorAppClient {
  constructor(
    private readonly store: BoardStore,
    private readonly api: CddApi,
    private readonly openWindow: (url: string) => void = url => void window.open(url, '_blank'),
  ) {}

  async openOn(editor: AppData, project: string): Promise<void> {
    const app = await AppClientGenerated.named(this.api, editor.label).open()
    if (!app) return
    if (app.status !== 'running') {
      this.store.toast(`The ${app.label} is ${app.status}: open it from the chat bar's status row, which starts it for that chat.`, true)
      return
    }
    const page = new URL(app.url)
    page.searchParams.set(PROJECT_QUERY, project)
    this.openWindow(page.toString())
  }
}
