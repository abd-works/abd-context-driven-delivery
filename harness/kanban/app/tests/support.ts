import { expect } from '@playwright/test'
import type { APIRequestContext, Locator, Page } from '@playwright/test'

export const BOARD_POST_HEADERS = { 'X-CDD-Board': '1' }
export const ACCENT = 'rgb(229, 83, 26)'
const CHAT_POLL_MILLISECONDS = 300

export async function openBoard(page: Page): Promise<void> {
  await page.goto('/')
  await expect(page.locator('.board-column').first()).toBeVisible({ timeout: 20_000 })
}

export const card = (page: Page, ticket: string): Locator => page.locator(`.ticket-card[data-ticket="${ticket}"]`)

// A person grabs a card by its title; a drag cannot start on the buttons further down it.
export const BY_ITS_TITLE = { x: 24, y: 14 }

export const openCard = (page: Page, ticket: string): Locator => page.locator(`[data-open-card="${ticket}"]`)

export const toast = (page: Page, text: string | RegExp): Locator => page.locator('.toast').filter({ hasText: text })

export async function openCardOf(page: Page, ticket: string): Promise<Locator> {
  await card(page, ticket).locator('.card-mark').first().click()
  const opened = openCard(page, ticket)
  await expect(opened).toBeVisible()
  return opened
}

// An opened card shows its tiles only; pressing a tile's name opens that tile's action bar.
export async function openTileBarOf(opened: Locator): Promise<Locator> {
  await opened.locator('.tile-name').first().click()
  const bar = opened.locator('.expansion').first()
  await expect(bar).toBeVisible()
  return bar
}

export async function turnOffActiveSessionOnly(page: Page): Promise<void> {
  await page.getByRole('switch', { name: 'Active session only' }).uncheck()
}

// A chat with the cdd-board mod loaded, as the server sees one: it polls for what to do and says whether a turn is running.
export class FakeChat {
  readonly received: { kind: string; text: string }[] = []
  isBusy = false
  readonly id: string
  readonly name: string
  private readonly request: APIRequestContext
  private timer: ReturnType<typeof setInterval> | undefined

  constructor(request: APIRequestContext, chat: string, name: string) {
    this.request = request
    this.id = chat
    this.name = name
  }

  private async poll(): Promise<void> {
    const answer = await this.request.post(`/api/chats/${this.id}/next`, { headers: BOARD_POST_HEADERS, data: { is_busy: this.isBusy, name: this.name } })
    const command = (await answer.json()) as { kind: string; text: string } | null
    if (command) this.received.push(command)
  }

  async start(): Promise<void> {
    await this.poll()
    this.timer = setInterval(() => void this.poll().catch(() => undefined), CHAT_POLL_MILLISECONDS)
  }

  stop(): void {
    clearInterval(this.timer)
  }
}
