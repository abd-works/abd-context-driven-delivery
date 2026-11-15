import { PROJECT_HEADER, projectOfPage, type CddApi } from '@cdd/cdd-shared'

import { API_ROOT } from '@src/session-board/board-server-paths'

import type { BoardStore } from '../shared/board-store'

const BOARD_HEADER = 'X-CDD-Board'
const NOT_CONNECTED = 503
// A call still running after this long says so: the shared cdd server can be busy for minutes.
const SLOW_CALL_MILLISECONDS = 8_000
// How much of a body that is not JSON the failure quotes.
const SHOWN_BODY_CHARACTERS = 200

export type Send = (path: string, init?: RequestInit) => Promise<Response>

export const sendWithFetch: Send = (path, init) => fetch(path, init)

export const BOARD_SERVER_DOWN = 'The session board server is not answering.'

// Where the page sends what failed: PageFailures shows it and tells the chat that opened the page.
export type Failures = {
  fail(failure: string, context: string): void
  serverDown(failure: string, context: string): void
}


// Every call the page makes to its server, so a failure goes to one place, the page's failures, which show it and tell
// the chat that opened the page. A failed call answers null. The generated clients post through it.
export class BoardApi implements CddApi {
  constructor(
    private readonly store: BoardStore,
    private readonly failures: Failures,
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
    // fetch rejects only when no server answered at all, which is what BOARD_SERVER_DOWN says.
    const response = await this.send(`${API_ROOT}${path}`, init)
      .catch(() => null)
      .finally(() => clearTimeout(slow))
    if (!response) {
      this.failures.serverDown(BOARD_SERVER_DOWN, this.contextOf(path))
      return null
    }
    const body = this.parsed<T & { error?: string }>(await response.text(), path)
    if (body === undefined) return null
    if (response.ok) return this.accepted(body)
    this.refused(response.status, body?.error ?? `The server answered ${response.status}.`, path)
    return null
  }

  // A tool that answers nothing sends an empty body, which is null; a body that is not JSON is a failure the page shows,
  // answered as undefined so the call answers null.
  private parsed<Body>(text: string, path: string): Body | null | undefined {
    if (!text) return null
    try {
      return JSON.parse(text) as Body
    } catch (failure) {
      if (!(failure instanceof SyntaxError)) throw failure
      this.failures.fail(`The server answered ${path} with something that is not JSON: ${text.slice(0, SHOWN_BODY_CHARACTERS)}`, this.contextOf(path))
      return undefined
    }
  }

  private contextOf(path: string): string {
    return this.saysWhenSlow ? `Calling ${path} from the Kanban board` : `Reading ${path} again every two seconds on the Kanban board`
  }

  private waitingOn(path: string): void {
    this.store.toast(`Still waiting on ${path.slice(1)}: the cdd server is busy, so it can take a while.`)
  }

  // A route that reaches cdd answered, so cdd is back.
  private accepted<T>(body: T): T {
    if (this.store.state.serverFailure) this.store.change({ serverFailure: null })
    return body
  }

  private refused(status: number, error: string, path: string): void {
    if (status === NOT_CONNECTED) this.failures.serverDown(error, this.contextOf(path))
    else this.failures.fail(error, this.contextOf(path))
  }
}
