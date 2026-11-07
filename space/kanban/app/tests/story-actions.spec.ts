import { appendFileSync, rmSync, writeFileSync } from 'node:fs'
import { EOL } from 'node:os'
import { join } from 'node:path'

import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'

import { fixtureRoot, resetSessions } from '../test-utils/fixture-repo'
import { BOARD_POST_HEADERS, card, FakeChat, openBoard, openCardOf, openTileBarOf, startBoard, toast, turnOffActiveSessionOnly } from './support'

const BROKEN_BOARD_PORT = 8781

// A spec per story that acts, each against the real server, the real cdd tools, and the throwaway repository.
// The specs share that repository, so each works on its own ticket, and the session changes come last.
const CARD_CORNER = { x: 6, y: 6 }
let chat: FakeChat

const column = (page: Page, name: string) => page.locator(`.board-column[data-column="${name}"]`)

async function waitForChat(page: Page): Promise<void> {
  await expect(page.getByRole('combobox', { name: 'Chat to send commands to' })).toHaveValue(chat.id, { timeout: 10_000 })
}

async function showTicket(page: Page, ticket: string): Promise<void> {
  await card(page, ticket).click({ position: CARD_CORNER })
}

async function lastReceived(text: string): Promise<void> {
  await expect.poll(() => chat.received.map(command => command.text), { timeout: 8_000 }).toContain(text)
}

async function receivedContaining(words: string, count: number): Promise<void> {
  await expect.poll(() => chat.received.filter(command => command.text.includes(words)).length, { timeout: 8_000 }).toBe(count)
}

test.beforeAll(async ({ playwright, baseURL }) => {
  const request = await playwright.request.newContext({ baseURL })
  chat = new FakeChat(request, 'surface-chat', 'Surface chat')
  await chat.start()
})

test.afterAll(() => {
  chat.stop()
})

test.beforeEach(async ({ page }) => {
  await openBoard(page)
})

test.describe('Restrict Actions To Active Session', () => {
  // A move runs nothing in a chat, so only what runs in the session's chat waits for the ticket to be active.
  test('should let a ticket that is not active be dragged, activated, and its files opened', async ({ page }) => {
    const billing = card(page, 'billing-report')
    await expect(billing).toHaveAttribute('draggable', 'true')
    await expect(billing.getByRole('button', { name: 'Activate' })).toBeEnabled()
    await billing.getByRole('button', { name: 'folder' }).click()
    await expect(page.locator('[data-panel="files"]')).toBeVisible()
  })

  test('should keep its practice switches off until Active session only is turned off', async ({ page }) => {
    await showTicket(page, 'billing-report')
    const practiceSwitch = page.getByRole('switch', { name: 'Disable UX for Billing report' })
    await expect(practiceSwitch).toBeDisabled()
    await turnOffActiveSessionOnly(page)
    await expect(practiceSwitch).toBeEnabled()
  })
})

test.describe('Add Backlog Item', () => {
  test('should keep Add off with no title', async ({ page }) => {
    await page.getByRole('button', { name: 'New backlog ticket' }).click()
    await expect(page.getByRole('button', { name: 'Add', exact: true })).toBeDisabled()
    await page.getByRole('button', { name: 'Cancel' }).click()
    await expect(page.getByRole('textbox', { name: 'Title' })).toHaveCount(0)
  })
})

test.describe('Set Stage WIP Limit', () => {
  test('should close the field on Escape without changing the limit', async ({ page }) => {
    await page.getByRole('button', { name: 'WIP limit for Specification is 3. Edit' }).click()
    await page.getByRole('spinbutton', { name: 'WIP limit for Specification' }).fill('9')
    await page.getByRole('spinbutton', { name: 'WIP limit for Specification' }).press('Escape')
    await expect(page.getByRole('button', { name: 'WIP limit for Specification is 3. Edit' })).toBeVisible()
  })

  test('should save the field on leaving it', async ({ page }) => {
    await page.getByRole('button', { name: 'WIP limit for Implementation is 3. Edit' }).click()
    await page.getByRole('spinbutton', { name: 'WIP limit for Implementation' }).fill('5')
    await page.getByRole('heading', { level: 2 }).first().click()
    await expect(page.getByRole('button', { name: 'WIP limit for Implementation is 5. Edit' })).toBeVisible()
  })
})

test.describe('Send commands to a chat', () => {
  test('should show a chat by the name its mod reports, and keep its id to send to', async ({ page }) => {
    await waitForChat(page)
    await expect(page.getByRole('option', { name: 'Surface chat' })).toHaveAttribute('value', 'surface-chat')
  })

  test('should pick the only chat and say a fill is queued', async ({ page }) => {
    await waitForChat(page)
    await card(page, 'checkout-flow').getByRole('button', { name: 'Handoff' }).first().click()
    await expect(toast(page, /^Queued for the prompt/)).toBeVisible()
    await lastReceived('Write a handoff for ticket checkout-flow with /space-session-handoff-session.')
    expect(chat.received.at(-1)?.kind).toBe('fill')
  })

  test('should hold a fill at the server until the turn ends', async ({ page }) => {
    await waitForChat(page)
    chat.isBusy = true
    await expect(page.getByRole('option', { name: 'Surface chat (busy)' })).toBeAttached({ timeout: 8_000 })
    const before = chat.received.length
    await card(page, 'checkout-flow').getByRole('button', { name: 'Split' }).first().click()
    await expect(toast(page, 'It goes in when this turn ends.')).toBeVisible()
    expect(chat.received.length).toBe(before)
    chat.isBusy = false
    await expect.poll(() => chat.received.length).toBeGreaterThan(before)
    expect(chat.received.at(-1)?.kind).toBe('fill')
  })
})

test.describe('Generate Fidelity Output', () => {
  test('should send the generate command from Run on an opened card', async ({ page }) => {
    await waitForChat(page)
    const bar = await openTileBarOf(await openCardOf(page, 'checkout-flow'))
    await bar.getByRole('button', { name: /^diagram/ }).click()
    await bar.getByRole('button', { name: 'Run' }).click()
    await expect.poll(() => chat.received.map(command => command.text).join('\n')).toContain('/actions-generate')
    expect(chat.received.at(-1)?.kind).toBe('command')
  })
})

test.describe('Send Tile Action To Chat', () => {
  test('should send the chosen action on a tile', async ({ page }) => {
    await waitForChat(page)
    const tile = page.locator('.details-body [data-tile="stories-story-map"]')
    await tile.getByRole('button', { name: 'story-map', exact: true }).click()
    await tile.getByRole('combobox', { name: 'Action' }).selectOption('sketch')
    await tile.getByRole('button', { name: /^code|^diagram|^markdown/ }).first().click()
    await tile.getByRole('button', { name: 'Run' }).click()
    await lastReceived('/actions-sketch stories-story-map session=.sessions/checkout-flow/session.json')
  })
})

test.describe('Open Practice Tile', () => {
  // Moving across the details grid would otherwise open bar after bar, so there a tile opens only on a press.
  test('should leave a tile in the details closed while the pointer only rests on it', async ({ page }) => {
    const tile = page.locator('.details-body [data-tile="ddd-bounded-context"]')
    await tile.hover()
    await page.waitForTimeout(800)
    await expect(tile.locator('.expansion')).toHaveCount(0)
  })

  test('should keep a pressed tile open after the pointer leaves', async ({ page }) => {
    const tile = page.locator('.details-body [data-tile="ddd-bounded-context"]')
    await tile.getByRole('button', { name: 'bounded-context', exact: true }).click()
    await expect(tile.locator('.expansion')).toBeVisible()
    await page.locator('.board-header').hover()
    await page.waitForTimeout(400)
    await expect(tile.locator('.expansion')).toBeVisible()
  })

  test('should keep two pressed tiles open at once', async ({ page }) => {
    const details = page.locator('.details-body')
    await details.locator('[data-tile="ddd-bounded-context"]').getByRole('button', { name: 'bounded-context', exact: true }).click()
    await details.locator('[data-tile="stories-story-map"]').getByRole('button', { name: 'story-map', exact: true }).click()
    await expect(details.locator('[data-tile="ddd-bounded-context"] .expansion, [data-tile="stories-story-map"] .expansion')).toHaveCount(2)
  })
})

test.describe('Expand Ticket', () => {
  test('should open a card on the fidelity of a pressed segment', async ({ page }) => {
    await card(page, 'checkout-flow').getByRole('button', { name: /practices-ddd-ddd-bounded-context/ }).first().click()
    const opened = page.locator('[data-open-card="checkout-flow"]')
    await expect(opened.locator('[data-tile="ddd-bounded-context"] .expansion')).toBeVisible()
  })

  test('should show the skill of the segment under the pointer', async ({ page }) => {
    await card(page, 'checkout-flow').getByRole('button', { name: /practices-ux-ux-ia/ }).first().hover()
    await expect(card(page, 'checkout-flow').getByText('/practices-ux-ux-ia')).toBeVisible()
  })

  test('should expand only one card at a time', async ({ page }) => {
    await openCardOf(page, 'checkout-flow')
    await openCardOf(page, 'billing-report')
    await expect(page.locator('.card-open')).toHaveCount(1)
  })
})

test.describe('Display Ticket Details', () => {
  test('should show the ticket of a card pressed anywhere', async ({ page }) => {
    await card(page, 'billing-report').getByRole('button', { name: 'Show Billing report' }).click({ position: { x: 4, y: 4 } })
    await expect(page.getByRole('heading', { name: 'Billing report' })).toBeVisible()
  })

  test('should show a closed ticket with Complete as its place', async ({ page }) => {
    await showTicket(page, 'shipped-work')
    await expect(page.locator('.details-place').first()).toHaveText(/Complete/)
  })
})

test.describe('Choose Ticket Practices', () => {
  test('should turn a practice off, say where it was saved, and fade its tile', async ({ page }) => {
    await page.getByRole('switch', { name: 'Disable UX for Checkout flow' }).click()
    await expect(toast(page, 'UX off for Checkout flow · saved to .sessions/checkout-flow/session.json')).toBeVisible()
    await expect(page.locator('.details-body [data-tile="ux-ia"]')).toHaveCSS('opacity', '0.12')
    await page.getByRole('button', { name: 'Hide practices not enabled' }).click()
    await expect(page.locator('.details-body [data-tile="ux-ia"]')).toHaveCount(0)
    await page.getByRole('button', { name: 'Show practices not enabled' }).click()
    await page.getByRole('switch', { name: 'Enable UX for Checkout flow' }).click()
    await expect(toast(page, 'UX on for Checkout flow')).toBeVisible()
  })
})

test.describe('Arrange Board And Details', () => {
  test('should give the board more height on a drag, and never close the details', async ({ page }) => {
    const before = (await page.locator('.board-region').boundingBox())!.height
    const grip = (await page.locator('.grip').boundingBox())!
    await page.mouse.move(grip.x + 200, grip.y + 7)
    await page.mouse.down()
    await page.mouse.move(grip.x + 200, grip.y + 107, { steps: 4 })
    expect((await page.locator('.board-region').boundingBox())!.height).toBe(before + 100)
    await page.mouse.move(grip.x + 200, 890, { steps: 4 })
    await page.mouse.up()
    expect((await page.locator('.details-region').boundingBox())!.height).toBeGreaterThanOrEqual(160)
  })

  test('should give a region the whole page and bring the other back', async ({ page }) => {
    await page.getByRole('button', { name: 'Expand board' }).click()
    await expect(page.locator('.details-region')).toHaveCount(0)
    await page.getByRole('button', { name: 'Collapse board' }).click()
    await page.getByRole('button', { name: 'Expand details' }).click()
    await expect(page.locator('.board-region')).toHaveCount(0)
    await page.getByRole('button', { name: 'Collapse details' }).click()
    await expect(page.locator('.board-region')).toBeVisible()
  })
})

test.describe('Arrange Side Panel', () => {
  test.beforeEach(async ({ page }) => {
    await page.getByRole('button', { name: 'Stories', exact: true }).click()
    await expect(page.locator('[data-panel="help"]')).toBeVisible()
  })

  test('should set a panel\'s width on a drag of its left edge', async ({ page }) => {
    const panel = page.locator('[data-panel="help"]')
    const before = (await panel.boundingBox())!
    await page.mouse.move(before.x, 400)
    await page.mouse.down()
    await page.mouse.move(before.x - 100, 400, { steps: 4 })
    await page.mouse.up()
    expect((await panel.boundingBox())!.width).toBe(before.width + 100)
  })

  test('should keep the columns\' width and scroll them sideways when a panel opens', async ({ page }) => {
    const region = page.locator('.board-region')
    await expect(region.evaluate(element => element.scrollWidth > element.clientWidth)).resolves.toBe(true)
    expect((await page.locator('.column-grid').first().boundingBox())!.width).toBeGreaterThanOrEqual(1488)
  })

  test('should let an expanded panel take the board\'s place, and × close it', async ({ page }) => {
    await page.getByRole('button', { name: 'Expand help' }).click()
    await expect(page.locator('.board-main')).toBeHidden()
    expect((await page.locator('[data-panel="help"]').boundingBox())!.width).toBe(1600)
    await page.getByRole('button', { name: 'Collapse help' }).click()
    await expect(page.locator('.board-main')).toBeVisible()
    await page.getByRole('button', { name: 'Close help' }).click()
    await expect(page.locator('[data-panel="help"]')).toHaveCount(0)
  })
})

test.describe('Open Help', () => {
  test('should show a fidelity\'s overview, guidance, rules, and Forge link', async ({ page }) => {
    await page.locator('.details-body').getByRole('button', { name: 'Help for story-map' }).click()
    const help = page.locator('[data-panel="help"]')
    await expect(help.getByRole('heading', { name: 'story-map' })).toBeVisible()
    await expect(help.getByText('GUIDANCE')).toBeVisible()
    await expect(help.getByText('RULES', { exact: false }).first()).toBeVisible()
    await expect(help.getByRole('link', { name: 'Forge' })).toHaveAttribute('href', /forge\.abdworks\.net/)
  })

  test('should head a practice\'s rules SHARED RULES and say Practice overview', async ({ page }) => {
    await page.getByRole('button', { name: 'DDD', exact: true }).click()
    const help = page.locator('[data-panel="help"]')
    await expect(help.getByText('Practice overview')).toBeVisible()
    await expect(help.locator('.panel-kind').filter({ hasText: 'SHARED RULES' })).toBeVisible()
  })
})

test.describe('Open Validation Report', () => {
  test('should show the rules with the failing line marked', async ({ page }) => {
    await page.locator('.details-body [data-tile="stories-story-map"]').getByRole('button', { name: 'violations' }).click()
    const report = page.locator('[data-panel="report"]')
    await expect(report.getByRole('button', { name: /verb-noun-format/ })).toBeVisible()
    await expect(report.locator('.code-line.is-failing')).toContainText('Handle Payment')
  })

  test('should open a violation\'s file at its line in the Files panel', async ({ page }) => {
    await card(page, 'checkout-flow').getByRole('button', { name: 'Run next: review violations' }).first().click()
    await page.locator('[data-panel="report"]').getByRole('button', { name: '.context/story-map.md:6', exact: true }).click()
    const files = page.locator('[data-panel="files"]')
    await expect(files.getByRole('tab', { name: 'story-map.md' })).toBeVisible()
    await expect(files.locator('.code-line.is-failing')).toContainText('Handle Payment')
  })
})

test.describe('Fix Report Violations', () => {
  test('should send Fix and Fix all to the chat', async ({ page }) => {
    await waitForChat(page)
    await card(page, 'checkout-flow').getByRole('button', { name: 'Run next: review violations' }).first().click()
    const report = page.locator('[data-panel="report"]')
    await report.getByRole('button', { name: 'Fix .context/story-map.md:6' }).click()
    await receivedContaining('of the stories-story-map rule.', 1)
    await report.getByRole('button', { name: 'Fix all', exact: true }).click()
    await receivedContaining('Fix all violations of verb-noun-format found in this report', 1)
  })

  test('should send Fix all violations to the chat as the report it names', async ({ page }) => {
    await waitForChat(page)
    await card(page, 'checkout-flow').getByRole('button', { name: 'Run next: review violations' }).first().click()
    await page.locator('[data-panel="report"]').getByRole('button', { name: 'Fix all violations', exact: true }).click()
    await receivedContaining('Fix all violations found in this report: .sessions/checkout-flow/validation-reports/', 1)
  })
})

test.describe('Display Violations Band', () => {
  test('should name the active ticket\'s violations across the page top', async ({ page }) => {
    await expect(page.getByRole('status', { name: "Active ticket's violations" })).toContainText('checkout-flow · Discovery · violations: stories-story-map')
  })
})

test.describe('List, browse, and view files', () => {
  test('should show the two modes of the files panel', async ({ page }) => {
    await card(page, 'checkout-flow').getByRole('button', { name: 'folder' }).first().click()
    const files = page.locator('[data-panel="files"]')
    await expect(files.getByText('.context/', { exact: true })).toBeVisible()
    await files.getByRole('button', { name: 'files', exact: true }).click()
    await expect(files.getByRole('tab', { name: 'story-map.md' })).toBeVisible()
    await expect(files.locator('.file-lines')).toContainText('Check Out Order')
  })

  test('should offer a tab for a format not generated yet and say so', async ({ page }) => {
    await page.locator('.details-body [data-tile="stories-story-map"]').getByRole('button', { name: 'story-map', exact: true }).click()
    await page.locator('.details-body [data-tile="stories-story-map"] .expansion').getByRole('button', { name: 'files', exact: true }).click()
    const files = page.locator('[data-panel="files"]')
    await files.getByRole('tab', { name: 'story-map.drawio' }).click()
    await expect(files.locator('.file-lines')).toContainText('Not generated yet.')
  })
})

test.describe('Refresh Board After Tool Calls', () => {
  test('should show a move made elsewhere with a toast', async ({ page, request }) => {
    await request.post('/api/ticket/pricing-rules/move-next', { headers: BOARD_POST_HEADERS })
    await expect(toast(page, 'Pricing rules moved to Specification · Done')).toBeVisible({ timeout: 8_000 })
    await expect(column(page, 'Specification').locator('.card-list').nth(1).locator('[data-ticket="pricing-rules"]')).toBeVisible()
  })

  test('should read an open files list again when the board changes', async ({ page }) => {
    await card(page, 'checkout-flow').getByRole('button', { name: 'folder' }).first().click()
    const files = page.locator('[data-panel="files"]')
    await expect(files.getByRole('button', { name: 'story-map.md', exact: true })).toBeVisible()
    writeFileSync(join(fixtureRoot, '.context', 'story-map.drawio'), `<mxfile />${EOL}`, 'utf-8')
    appendFileSync(join(fixtureRoot, '.sessions', 'checkout-flow', 'session.log'), `2026-11-01T11:00:00Z generate /work stories story_map drawio stories no-chat${EOL}`, 'utf-8')
    await expect(files.getByRole('button', { name: 'story-map.drawio', exact: true })).toBeVisible({ timeout: 8_000 })
  })
})

test.describe('Display Connected Status', () => {
  // A board of its own, whose cdd cannot start because the program it names does not exist.
  test('should show a band when cdd cannot be reached', async ({ page }) => {
    const board = await startBoard(BROKEN_BOARD_PORT, { CDD_PYTHON: join(fixtureRoot, 'no-such-python.exe') })
    try {
      await page.goto(board.url)
      await expect(page.locator('.band-failure')).toContainText('cdd is not connected', { timeout: 15_000 })
    } finally {
      board.stop()
    }
  })

  test('should show no band while cdd answers', async ({ page }) => {
    await expect(page.locator('.column-grid').first()).toBeVisible()
    await expect(page.locator('.band-failure')).toHaveCount(0)
  })

  // The ticket a violation belongs to is gone, so session.read_file really refuses it.
  test('should show a tool failure in a toast', async ({ page }) => {
    await card(page, 'checkout-flow').getByRole('button', { name: 'Run next: review violations' }).first().click()
    const violation = page.locator('[data-panel="report"]').getByRole('button', { name: '.context/story-map.md:6', exact: true })
    await expect(violation).toBeVisible()
    rmSync(join(fixtureRoot, '.sessions', 'checkout-flow'), { recursive: true, force: true })
    try {
      await violation.click()
      await expect(toast(page, /no session at '\.sessions\/checkout-flow\/session\.json'/)).toBeVisible()
    } finally {
      resetSessions(fixtureRoot)
    }
  })
})

test.describe('Choose Session Root', () => {
  // Choosing a root changes the shared fixture's session, so this only browses and cancels.
  test("should open the roots from the details bar and browse the repository's folders for the session root", async ({ page }) => {
    await page.locator('.details-bar').getByRole('button', { name: 'whole repository' }).click()
    const roots = page.getByRole('dialog')
    await expect(roots.getByRole('heading', { name: 'Roots of Checkout flow' })).toBeVisible()
    await roots.getByRole('button', { name: 'Change the root of Session' }).click()
    await expect(roots.getByRole('listitem').filter({ hasText: 'app/' })).toBeVisible()
    await roots.getByRole('button', { name: 'Cancel' }).click()
    await expect(roots.getByRole('button', { name: 'Change the root of Stories' })).toBeVisible()
  })
})

test.describe('Activate Ticket', () => {
  test('should switch the session from the dialog, with merge off', async ({ page }) => {
    await card(page, 'billing-report').getByRole('button', { name: 'Activate' }).first().click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.getByRole('heading', { name: 'Switch from Checkout flow to Billing report' })).toBeVisible()
    await expect(dialog.getByRole('checkbox', { name: 'Merge Checkout flow into main' })).not.toBeChecked()
    await expect(dialog.getByRole('checkbox', { name: 'Create branch billing-report' })).toBeChecked()
    await dialog.getByRole('button', { name: 'Activate' }).click()
    await expect(toast(page, 'Billing report is now active')).toBeVisible({ timeout: 15_000 })
    await expect(page.locator('.header-active')).toHaveText('Billing report')
  })
})

test.describe('Close Active Session', () => {
  test('should send the close session command to the chat', async ({ page }) => {
    await waitForChat(page)
    await card(page, 'billing-report').getByRole('button', { name: 'Close' }).first().click()
    await lastReceived('/space:session:close-session')
  })

  test('should leave the ticket in its column', async ({ page }) => {
    await waitForChat(page)
    await card(page, 'billing-report').getByRole('button', { name: 'Close' }).first().click()
    await lastReceived('/space:session:close-session')
    await expect(column(page, 'Complete').locator('[data-ticket="billing-report"]')).toHaveCount(0)
  })
})
