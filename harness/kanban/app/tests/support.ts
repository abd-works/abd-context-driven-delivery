import { spawn, type ChildProcess } from 'node:child_process'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { expect } from '@playwright/test'
import type { APIRequestContext, Locator, Page } from '@playwright/test'

import { fixtureRoot } from '../test-utils/fixture-repo'

export const BOARD_POST_HEADERS = { 'X-CDD-Board': '1' }
export const ACCENT = 'rgb(229, 83, 26)'
const CHAT_POLL_MILLISECONDS = 300
const APP_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const BOARD_STARTED_MILLISECONDS = 30_000

// A board of a spec's own on the throwaway repository, started with the environment the spec gives it, so a spec can
// make cdd fail for real: a CDD_PYTHON that names no program leaves the board with a cdd that cannot start.
export async function startBoard(port: number, env: Record<string, string> = {}): Promise<{ url: string; stop: () => void }> {
  const board: ChildProcess = spawn(process.execPath, [join(APP_ROOT, 'node_modules', 'tsx', 'dist', 'cli.mjs'), 'packages/session-board/serve.ts'], {
    cwd: APP_ROOT,
    env: { ...process.env, BOARD_PORT: String(port), BOARD_PROJECT: fixtureRoot, ...env },
    stdio: 'ignore',
  })
  const url = `http://127.0.0.1:${port}`
  await expect.poll(() => fetch(url).then(answer => answer.ok).catch(() => false), { timeout: BOARD_STARTED_MILLISECONDS }).toBe(true)
  return { url, stop: () => board.kill() }
}

export async function openBoard(page: Page): Promise<void> {
  await page.goto('/')
  await expect(page.locator('.board-column').first()).toBeVisible({ timeout: 20_000 })
}

export const card = (page: Page, ticket: string): Locator => page.locator(`.ticket-card[data-ticket="${ticket}"]`)

// A person grabs a card by its title; a drag cannot start on the buttons further down it.
const BY_ITS_TITLE = { x: 24, y: 14 }
const DRAG_STEPS = 10

// Drags a card by its title onto a list the way a person does, in small moves. Playwright's dragTo jumps to the target
// in one move, and a drag made that way was sometimes never dropped against the whole stack.
export async function dragCard(page: Page, dragged: Locator, target: Locator): Promise<void> {
  const from = (await dragged.boundingBox())!
  const to = (await target.boundingBox())!
  await page.mouse.move(from.x + BY_ITS_TITLE.x, from.y + BY_ITS_TITLE.y)
  await page.mouse.down()
  await page.mouse.move(from.x + BY_ITS_TITLE.x + 20, from.y + BY_ITS_TITLE.y + 10, { steps: DRAG_STEPS })
  await page.mouse.move(to.x + to.width / 2, to.y + Math.min(to.height / 2, 60), { steps: DRAG_STEPS })
  await page.mouse.up()
}

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

// A chat with the cdd-board mod loaded, as cdd sees one: it checks in, says whether a turn is running, and takes its commands.
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
    const answer = await this.request.post(`/api/chat/${this.id}/check-in`, { headers: BOARD_POST_HEADERS, data: { is_busy: this.isBusy, name: this.name } })
    const commands = (await answer.json()) as { kind: string; text: string }[]
    this.received.push(...commands)
  }

  async start(): Promise<void> {
    await this.poll()
    this.timer = setInterval(() => void this.poll().catch(() => undefined), CHAT_POLL_MILLISECONDS)
  }

  stop(): void {
    clearInterval(this.timer)
  }
}
