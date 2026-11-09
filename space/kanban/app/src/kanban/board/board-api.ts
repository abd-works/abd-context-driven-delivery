import type { BoardStore } from '../shared/board-store'

const BOARD_HEADER = 'X-CDD-Board'
const API_ROOT = '/api'
const NOT_CONNECTED = 503
// A call still running after this long says so: the shared cdd server can be busy for minutes.
const SLOW_CALL_MILLISECONDS = 8_000
// The board's own read runs every two seconds, so it says nothing when slow.
const BOARD_READ = '/board/show'

export type Send = (path: string, init?: RequestInit) => Promise<Response>

const sendWithFetch: Send = (path, init) => fetch(path, init)

export const pathPart = (text: string): string => encodeURIComponent(text)

// Every call the page makes to its server, so a failure is shown to the person in one place. A failed call answers null.
export class BoardApi {
  constructor(
    private readonly store: BoardStore,
    private readonly send: Send = sendWithFetch,
  ) {}

  // A route the board server answers itself, such as its build: the answer says nothing about whether cdd is back.
  get<T>(path: string): Promise<T | null> {
    return this.call<T>(path, undefined, false)
  }

  post<T>(path: string, body: unknown = {}): Promise<T | null> {
    return this.call<T>(path, { method: 'POST', headers: { [BOARD_HEADER]: '1', 'Content-Type': 'application/json' }, body: JSON.stringify(body) }, true)
  }

  private async call<T>(path: string, init: RequestInit | undefined, reachesCdd: boolean): Promise<T | null> {
    const slow = path === BOARD_READ ? undefined : setTimeout(() => this.waitingOn(path), SLOW_CALL_MILLISECONDS)
    const response = await this.send(`${API_ROOT}${path}`, init)
      .catch(() => null)
      .finally(() => clearTimeout(slow))
    if (!response) {
      this.store.change({ serverFailure: 'The session board server is not answering.' })
      return null
    }
    const body = (await response.json().catch(() => null)) as (T & { error?: string }) | null
    if (response.ok) return reachesCdd ? this.accepted(body) : body
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
