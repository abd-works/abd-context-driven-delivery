import { BoardClientGenerated, type BoardData } from '@cdd/space/kanban/board'

import type { BoardPage } from './board-page'
import { PendingChanges, type PendingChange } from '../shared/pending-changes'

const POLL_MILLISECONDS = 2000

// Keeps the page's copy of the board current. The agent changes the board without telling the page, so it reads again.
export class BoardReader {
  private reads = 0
  private latestApplied = 0
  private isPolling = false
  // The board tool the reads go through, made at the first read, once the page has its api. It is not the page's board,
  // which stays the read it was made from until the store holds a new one, so announcements compare two reads.
  private source: BoardClientGenerated | null = null
  // The board as the server last answered it, before the changes the page shows ahead of it are laid over it.
  private latestRead: BoardData | null = null
  readonly pending = new PendingChanges()

  constructor(private readonly page: BoardPage) {}

  // Reads can overlap with a move's own read, so a slower, older answer never replaces a newer one.
  async refresh(): Promise<void> {
    const order = ++this.reads
    this.source ??= new BoardClientGenerated(this.page.api)
    const shown = await this.source.show()
    if (!shown || order < this.latestApplied) return
    this.latestApplied = order
    await this.apply(shown.toJSON())
  }

  // A change a person makes shows at once and stays over every read until one shows it; one the server refuses is taken
  // back, and the refusal is shown the way every failed call is.
  async change<T>(made: PendingChange, send: () => Promise<T | null>): Promise<T | null> {
    this.pending.add(made)
    this.redraw()
    const answer = await send()
    if (answer !== null) return answer
    this.pending.drop(made)
    this.redraw()
    return null
  }

  private redraw(): void {
    const read = this.latestRead ?? this.page.store.state.board
    if (read) this.page.store.change({ board: this.pending.over(read) })
  }

  private async apply(shown: BoardData): Promise<void> {
    const { store } = this.page
    const before = store.state.board ? this.page.board : null
    this.latestRead = shown
    store.change({ board: this.pending.over(shown), now: Date.now() })
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
