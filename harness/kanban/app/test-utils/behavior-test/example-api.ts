import type { BoardData } from '@cdd/harness/kanban/board'
import type { Page, Request, Route } from '@playwright/test'

export type ExampleAnswer = { body: unknown; board?: BoardData }
export type PostedExample = (posted: Record<string, unknown>) => ExampleAnswer
export type ExampleAnswers = Record<string, ExampleAnswer | PostedExample>

const NOT_FOUND = 404

const addressOf = (request: Request): string => {
  const { pathname, search } = new URL(request.url())
  return `${request.method()} ${pathname}${search}`
}

// Answers the page's /api calls from examples, so the Playwright tier needs no server state. An answer can name the board
// to show from then on, which is what a real move would have changed.
export class ExampleApi {
  private board: BoardData
  private readonly answers: ExampleAnswers

  constructor(board: BoardData, answers: ExampleAnswers = {}) {
    this.board = board
    this.answers = answers
  }

  async answerOn(page: Page): Promise<void> {
    await page.route('**/api/**', route => this.answer(route))
  }

  private async answer(route: Route): Promise<void> {
    const request = route.request()
    const address = addressOf(request)
    if (address === 'POST /api/board/show') return route.fulfill({ json: this.board })
    if (address === 'GET /api/chats') return route.fulfill({ json: [] })
    // An example keyed by the JSON it was sent wins, because one route reads different things for different arguments.
    const example = this.answers[`${address} ${request.postData() ?? ''}`] ?? this.answers[address]
    if (!example) return route.fulfill({ status: NOT_FOUND, json: { error: `no example for ${address}` } })
    const { body, board } = typeof example === 'function' ? example(request.postDataJSON() as Record<string, unknown>) : example
    this.board = board ?? this.board
    return route.fulfill({ json: body })
  }
}
