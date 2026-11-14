import { BOARD_SERVER_DOWN, type Send } from './board-api'
import type { BoardStore } from '../shared/board-store'

// The page itself, as the board server serves it now: its index names the hashed script of its build.
const SERVED_PAGE = '/'

// The build the page was loaded from. A page left open across a rebuild keeps running the old code, so once the server
// serves a different build the page asks to be loaded again. The page is a static file, so no route answers it.
export class BuildClient {
  private loaded: string | null = null

  constructor(
    private readonly store: BoardStore,
    private readonly send: Send,
  ) {}

  // The page the board server serves now, empty while it serves none; null when the server does not answer. The answer
  // says nothing about whether cdd is back.
  async served(): Promise<string | null> {
    const response = await this.send(SERVED_PAGE, { cache: 'no-store' }).catch(() => null)
    if (!response) {
      this.store.change({ serverFailure: BOARD_SERVER_DOWN })
      return null
    }
    return response.ok ? response.text() : ''
  }

  async check(): Promise<void> {
    const served = await this.served()
    if (served === null) return
    this.loaded ??= served
    if (served !== this.loaded) this.store.change({ isNewBuild: true })
  }
}
