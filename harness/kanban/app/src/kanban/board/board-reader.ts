import type { BoardData } from '@cdd/harness/kanban/board'

import type { BoardPage } from './board-page'

const POLL_MILLISECONDS = 2000

// Keeps the page's copy of the board current. The agent changes the board without telling the page, so it reads again.
export class BoardReader {
  private reads = 0
  private latestApplied = 0
  private isPolling = false

  constructor(private readonly page: BoardPage) {}

  // Reads can overlap with a move's own read, so a slower, older answer never replaces a newer one.
  async refresh(): Promise<void> {
    const order = ++this.reads
    const shown = await this.page.board.show()
    if (!shown || order < this.latestApplied) return
    this.latestApplied = order
    await this.apply(shown.toJSON())
  }

  private async apply(shown: BoardData): Promise<void> {
    const { store } = this.page
    const before = store.state.board ? this.page.board : null
    store.change({ board: shown, now: Date.now() })
    const after = this.page.board
    for (const announcement of before ? after.announcementsSince(before) : []) store.toast(announcement)
    if (JSON.stringify(before) !== JSON.stringify(after)) await this.page.reloadOpen()
  }

  startPolling(): () => void {
    const timer = setInterval(() => void this.poll(), POLL_MILLISECONDS)
    void this.poll()
    return () => clearInterval(timer)
  }

  // A read takes longer than the interval while the cdd server starts, so polls never stack up.
  private async poll(): Promise<void> {
    if (this.isPolling) return
    this.isPolling = true
    await this.refresh().finally(() => {
      this.isPolling = false
    })
  }
}
