import { PROJECT_HEADER, projectOfPage, type CddApi } from '@cdd/cdd-shared'

import { API_ROOT } from '@src/session-board/board-server-paths'

import type { BoardStore } from '../shared/board-store'

const BOARD_HEADER = 'X-CDD-Board'
const NOT_CONNECTED = 503
// A call still running after this long says so: the shared cdd server can be busy for minutes.
const SLOW_CALL_MILLISECONDS = 8_000

export type Send = (path: string, init?: RequestInit) => Promise<Response>

export const sendWithFetch: Send = (path, init) => fetch(path, init)

export const BOARD_SERVER_DOWN = 'The session board server is not answering.'


// Every call the page makes to its server, so a failure is shown to the person in one place. A failed call answers null.
// The generated clients post through it, and so do the board server's own two routes (board-server-paths.ts).
export class BoardApi implements CddApi {
  constructor(
    private readonly store: BoardStore,
    private readonly send: Send = sendWithFetch,
    private readonly project: string = projectOfPage(),
    // The board's own read runs every two seconds, so its api says nothing when a call is slow.
    private readonly saysWhenSlow = true,
  ) {}

  post<T>(path: string, body: unknown = {}): Promise<T | null> {
    return this.call<T>(path, { method: 'POST', headers: { [BOARD_HEADER]: '1', 'Content-Type': 'application/json', ...this.projectHeader() }, body: JSON.stringify(body) })
  }

  private projectHeader(): Record<string, string> {
    return this.project ? { [PROJECT_HEADER]: this.project } : {}
  }

  private async call<T>(path: string, init: RequestInit): Promise<T | null> {
    const slow = !this.saysWhenSlow ? undefined : setTimeout(() => this.waitingOn(path), SLOW_CALL_MILLISECONDS)
    const response = await this.send(`${API_ROOT}${path}`, init)
      .catch(() => null)
      .finally(() => clearTimeout(slow))
    if (!response) {
      this.store.change({ serverFailure: BOARD_SERVER_DOWN })
      return null
    }
    const body = (await response.json().catch(() => null)) as (T & { error?: string }) | null
    if (response.ok) return this.accepted(body)
    this.refused(response.status, body?.error ?? `The server answered ${response.status}.`)
    return null
  }

  private waitingOn(path: string): void {
    this.store.toast(`Still waiting on ${path.slice(1)}: the cdd server is busy, so it can take a while.`)
  }

  // A route that reaches cdd answered, so cdd is back.
  private accepted<T>(body: T): T {
    if (this.store.state.serverFailure) this.store.change({ serverFailure: null })
    return body
  }

  private refused(status: number, error: string): void {
    if (status === NOT_CONNECTED) this.store.change({ serverFailure: error })
    else this.store.toast(error, true)
  }
}
