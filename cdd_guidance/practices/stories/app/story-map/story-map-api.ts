import { PROJECT_HEADER, projectOfPage, type CddApi } from '@cdd/cdd-shared'

// Where the board's server answers the page's calls; the page is served beside it, under STORY_MAP_PAGE.
const STORY_MAP_API = '/api'
// The board's server refuses a changing call without this header, so a page on another site cannot post to it.
const BOARD_HEADER = 'X-CDD-Board'
const NOT_CONNECTED = 503
// How much of a body that is not JSON the failure quotes.
const SHOWN_BODY_CHARACTERS = 200
export const SERVER_DOWN = 'The cdd server is not answering, so nothing was saved. Start it again with /cdd-restart in a chat, or open the Kanban from the chat bar, then try again.'

export type Send = (path: string, init: RequestInit) => Promise<Response>
// What the page does with a failure: StoryMapFailures.fail shows it and sends it to the chat that opened the page.
export type Fail = (failure: string, context: string) => void

// Every call the Story UI makes to the board's server, which reaches the cdd server. A failed call shows the person
// what failed and how to fix it, through the page's fail, and answers null, so the page keeps showing the story map as
// Python last sent it rather than an edit that was never saved. One board server serves every repository,
// so each call names the repository the page's ?project= link names, as the board's own page does.
export class StoryMapApi implements CddApi {
  constructor(
    private readonly failed: Fail,
    private readonly send: Send = (path, init) => fetch(path, init),
    private readonly project: string = projectOfPage(),
  ) {}

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    const headers = { [BOARD_HEADER]: 'story-ui', 'Content-Type': 'application/json', ...(this.project ? { [PROJECT_HEADER]: this.project } : {}) }
    const init = { method: 'POST', headers, body: JSON.stringify(body) }
    // fetch rejects only when no server answered at all, which is what SERVER_DOWN says and how to fix it.
    const response = await this.send(`${STORY_MAP_API}${path}`, init).catch(() => null)
    if (!response) return this.refused(SERVER_DOWN, path)
    const text = await response.text()
    const answer = this.parsed<Result & { error?: string }>(text, path)
    if (answer === undefined) return null
    if (response.ok) return answer
    return this.refused(response.status === NOT_CONNECTED ? SERVER_DOWN : answer?.error ?? `The server answered ${response.status} to ${path}.`, path)
  }

  // A tool that answers nothing sends an empty body, which is null; a body that is not JSON is a failure the page shows,
  // answered as undefined so the call answers null.
  private parsed<Body>(text: string, path: string): Body | null | undefined {
    if (!text) return null
    try {
      return JSON.parse(text) as Body
    } catch (failure) {
      if (!(failure instanceof SyntaxError)) throw failure
      this.refused(`The server answered ${path} with something that is not JSON: ${text.slice(0, SHOWN_BODY_CHARACTERS)}`, path)
      return undefined
    }
  }

  private refused(message: string, path: string): null {
    this.failed(message, `Calling ${path} from the Story UI`)
    return null
  }
}
