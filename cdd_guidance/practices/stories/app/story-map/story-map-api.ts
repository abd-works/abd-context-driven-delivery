import { PROJECT_HEADER, projectOfPage, type CddApi } from '@cdd/cdd-shared'

import { STORY_MAP_API } from '../story-map-page'

// The board's server refuses a changing call without this header, so a page on another site cannot post to it.
const BOARD_HEADER = 'X-CDD-Board'
const NOT_CONNECTED = 503
export const SERVER_DOWN = 'The cdd server is not answering, so nothing was saved. Start it again with /cdd-restart in a chat, or open the Kanban from the chat bar, then try again.'

export type Send = (path: string, init: RequestInit) => Promise<Response>
export type FailureListener = (message: string) => void

// Every call the Story UI makes to the board's server, which reaches the cdd server. A failed call shows the person
// what failed and how to fix it, through the listener the page gives, and answers null, so the page keeps showing the
// story map as Python last sent it rather than an edit that was never saved. One board server serves every repository,
// so each call names the repository the page's ?project= link names, as the board's own page does.
export class StoryMapApi implements CddApi {
  constructor(
    private readonly failed: FailureListener,
    private readonly send: Send = (path, init) => fetch(path, init),
    private readonly project: string = projectOfPage(),
  ) {}

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    const headers = { [BOARD_HEADER]: 'story-ui', 'Content-Type': 'application/json', ...(this.project ? { [PROJECT_HEADER]: this.project } : {}) }
    const init = { method: 'POST', headers, body: JSON.stringify(body) }
    const response = await this.send(`${STORY_MAP_API}${path}`, init).catch(() => null)
    if (!response) return this.refused(SERVER_DOWN)
    const answer = (await response.json().catch(() => null)) as (Result & { error?: string }) | null
    if (response.ok) return answer
    return this.refused(response.status === NOT_CONNECTED ? SERVER_DOWN : answer?.error ?? `The server answered ${response.status} to ${path}.`)
  }

  private refused(message: string): null {
    this.failed(message)
    return null
  }
}
