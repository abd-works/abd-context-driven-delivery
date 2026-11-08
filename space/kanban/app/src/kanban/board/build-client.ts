import type { BoardApi } from './board-api'
import type { BoardStore } from '../shared/board-store'

const BUILD_PATH = '/build'

// The build the page was loaded from. A page left open across a rebuild keeps running the old code, so once the server
// serves a different build the page asks to be loaded again.
export class BuildClient {
  private loaded: string | null = null

  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
  ) {}

  async check(): Promise<void> {
    const served = await this.api.get<{ build: string }>(BUILD_PATH)
    if (!served) return
    this.loaded ??= served.build
    if (served.build !== this.loaded) this.store.change({ isNewBuild: true })
  }
}
