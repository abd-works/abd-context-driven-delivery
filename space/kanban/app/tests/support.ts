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

// A board whose columns hold more cards than its region shows scrolls them under the details, where no drag can reach
// them, so a spec that drags between far cards opens the board over the whole of a tall page.
const TALL_PAGE = { width: 1600, height: 1600 }

export async function openWholeBoard(page: Page): Promise<void> {
  await page.setViewportSize(TALL_PAGE)
  await openBoard(page)
  await page.getByRole('button', { name: 'Expand board' }).click()
}

export const card = (page: Page, ticket: string): Locator => page.locator(`.ticket-card[data-ticket="${ticket}"]`)

// A person grabs a card by its title; a drag cannot start on the buttons further down it.
const BY_ITS_TITLE = { x: 24, y: 14 }
const DRAG_STEPS = 10

// Where a drag grabs what it drags, and where on the target it lets go: by default a card by its title, onto the
// target's middle; a child's row is grabbed near its left end, and a card dropped above another lets go on its top edge.
export type DragPlaces = { grab?: { x: number; y: number }; onTop?: boolean }
const NEAR_THE_TOP_EDGE = 4
const BELOW_THE_LAST_CARD = 24

// Drags a card by its title onto a list the way a person does, in small moves. Playwright's dragTo jumps to the target
// in one move, and a drag made that way was sometimes never dropped against the whole stack.
export async function dragCard(page: Page, dragged: Locator, target: Locator, { grab = BY_ITS_TITLE, onTop = false }: DragPlaces = {}): Promise<void> {
  await holdOver(page, dragged, target, { grab, onTop })
  await page.mouse.up()
}

// Leaves the drag held over the target, before the drop, so a spec can see what the target shows while it is dragged over.
export async function holdOver(page: Page, dragged: Locator, target: Locator, { grab = BY_ITS_TITLE, onTop = false }: DragPlaces = {}): Promise<void> {
  // The board region scrolls, and a card below its visible part cannot be grabbed where it is drawn; a list's label,
  // where a drop lands on no card, is brought into view first, then the card if that left it out of view.
  const labels = target.locator(':scope.card-list > .list-label')
  if (await labels.count()) await labels.first().scrollIntoViewIfNeeded()
  await dragged.scrollIntoViewIfNeeded()
  const from = (await dragged.boundingBox())!
  await page.mouse.move(from.x + grab.x, from.y + grab.y)
  await page.mouse.down()
  await page.mouse.move(from.x + grab.x + 20, from.y + grab.y + 10, { steps: DRAG_STEPS })
  const to = (await target.boundingBox())!
  const [top, bottom] = await shownRange(page)
  // A drop on a card makes the dragged ticket its child, so a drag onto a list drops where no card is: on the list's
  // label while the board shows it, else below the list's cards.
  const isList = await target.evaluate(element => element.classList.contains('card-list'))
  const label = isList && (await labels.count()) ? await labels.first().boundingBox() : null
  const down = onTop ? NEAR_THE_TOP_EDGE : isList ? await belowTheLastCard(target, to) : Math.min(to.height / 2, 60)
  const y = label && label.y >= top && label.y + label.height <= bottom ? label.y + label.height / 2 : Math.max(top, Math.min(to.y + down, bottom))
  await page.mouse.move(to.x + to.width / 2, y, { steps: DRAG_STEPS })
}

// The part of the board region on screen, so a drop never lands above the board or on the details below it.
async function shownRange(page: Page): Promise<[number, number]> {
  const region = await page.locator('.board-region').boundingBox()
  return region ? [region.y + BELOW_THE_LAST_CARD, region.y + region.height - BELOW_THE_LAST_CARD] : [0, Number.POSITIVE_INFINITY]
}

// Just under the list's last card, where the list itself takes the drop.
async function belowTheLastCard(target: Locator, to: { y: number; height: number }): Promise<number> {
  const cards = target.locator(':scope > .ticket-card')
  const last = (await cards.count()) ? await cards.last().boundingBox() : null
  return Math.min(last ? last.y + last.height - to.y + BELOW_THE_LAST_CARD : to.height / 2, to.height - 2 * BELOW_THE_LAST_CARD)
}

export const openCard = (page: Page, ticket: string): Locator => page.locator(`[data-open-card="${ticket}"]`)

export const toast = (page: Page, text: string | RegExp): Locator => page.locator('.toast').filter({ hasText: text })

// A press on a card's empty area opens it as well, so a card already open is left open.
export async function openCardOf(page: Page, ticket: string): Promise<Locator> {
  if (!(await openCard(page, ticket).isVisible())) await card(page, ticket).locator('.card-mark').first().click()
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
