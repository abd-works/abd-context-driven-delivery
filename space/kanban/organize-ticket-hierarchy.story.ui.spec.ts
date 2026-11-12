/**
 * Organize Ticket Hierarchy at the browser tier: what a person does on the board page to arrange tickets under parents.
 *
 * Scenarios: harness/.context/stories/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md,
 * the stories Add Child Ticket, Display Child Tickets In Parent, Expand Parent Ticket, Detach Child Ticket, Reassign
 * Ticket Parent, and Place Parent At Leftmost Child Stage. The Python tiers replay them from
 * organize-ticket-hierarchy.story.shared.py; here each scenario is one test, done on the page.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/`, where the board reads it; a When does what the person does on the page, a child's row dragged out of its
 * parent's card or a card dragged onto another; a Then reads what the person sees, and the session.json the board keeps
 * a ticket's parent in.
 */
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

import { card, dragCard, expect, fixtureRoot, holdOver, openWholeBoard, resetSessions, test, toast, writeInto, writeSession } from './app/tests/story-ui'
import type { Page } from './app/tests/story-ui'

const sessions = join(fixtureRoot, '.sessions')
const IN_SPECIFICATION = '2026-11-01T10:00:00Z move Specification no-chat'
const DONE_IN_DISCOVERY = '2026-11-01T10:00:00Z done Discovery no-chat'
// A child's row is grabbed at its own middle-left, clear of its Edit text button.
const BY_ITS_ROW = { grab: { x: 12, y: 9 } }

// A child opened on the board may sit in its parent's session folder, so its session.json is found wherever it is.
function sessionJson(ticket: string): { parent?: string; pulled_out?: boolean } {
  const found = readdirSync(sessions, { recursive: true, encoding: 'utf-8' }).find(path => path.replace(/\\/g, '/').endsWith(`${ticket}/session.json`))
  return found ? JSON.parse(readFileSync(join(sessions, found), 'utf-8')) : {}
}

const row = (page: Page, parent: string, child: string) => card(page, parent).locator(`[data-child="${child}"]`).first()
const rowsOf = (page: Page, parent: string) => card(page, parent).locator(':scope > .child-rows > [data-child]')
const childrenLine = (page: Page, parent: string) => card(page, parent).locator(':scope > .child-rows > .children-toggle')
// A column's In progress list, dropped on at its label: its middle can be another card, which would take the drop.
const listOf = (page: Page, column: string) => page.locator(`.board-column[data-column="${column}"] .card-list .list-label`).first()
const cardIn = (page: Page, column: string, ticket: string) => page.locator(`.board-column[data-column="${column}"] .ticket-card[data-ticket="${ticket}"]`)
const titleSize = (page: Page, ticket: string) => card(page, ticket).locator(':scope > .ticket-title-line .ticket-title').evaluate(title => parseFloat(getComputedStyle(title).fontSize))

const seedChild = (name: string, title: string, extra: { log?: string[]; pulledOut?: boolean } = {}) => writeSession(fixtureRoot, { name, title, parent: 'checkout-flow', ...extra })

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('Add Child Ticket', () => {
  test('Add a child ticket by hand', async ({ page }) => {
    await openWholeBoard(page)
    await card(page, 'checkout-flow').getByRole('button', { name: 'Add child' }).first().click()
    const field = page.getByRole('textbox', { name: 'Child title' })
    await field.fill('Enter card details')
    await field.press('Enter')
    await expect(row(page, 'checkout-flow', 'enter-card-details')).toBeVisible({ timeout: 10_000 })
    expect(sessionJson('enter-card-details').parent).toBe('checkout-flow')
    await expect(card(page, 'enter-card-details')).toHaveCount(0)
  })

  test('Drag a ticket onto a parent', async ({ page }) => {
    writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
    await openWholeBoard(page)
    await dragCard(page, card(page, 'pet-visits'), card(page, 'checkout-flow'))
    await expect(row(page, 'checkout-flow', 'pet-visits')).toBeVisible({ timeout: 10_000 })
    await expect(card(page, 'pet-visits')).toHaveCount(0)
  })
})

test.describe('Display Child Tickets In Parent', () => {
  test("Stack a parent's children inside its card", async ({ page }) => {
    seedChild('enter-card-details', 'Enter card details')
    seedChild('confirm-order', 'Confirm order')
    await openWholeBoard(page)
    await expect(rowsOf(page, 'checkout-flow')).toHaveCount(2)
    // A row names its child only, no stage of its own.
    await expect(row(page, 'checkout-flow', 'enter-card-details')).toHaveText('Enter card details')
    await expect(row(page, 'checkout-flow', 'confirm-order')).toHaveText('Confirm order')
    expect(await titleSize(page, 'checkout-flow')).toBeLessThan(await titleSize(page, 'billing-report'))
    await expect(card(page, 'enter-card-details')).toHaveCount(0)
    await expect(card(page, 'confirm-order')).toHaveCount(0)
  })

  test('Keep a dashed row for a child pulled out of its parent', async ({ page }) => {
    seedChild('enter-card-details', 'Enter card details', { pulledOut: true, log: [IN_SPECIFICATION] })
    await openWholeBoard(page)
    await expect(cardIn(page, 'Specification', 'enter-card-details')).toBeVisible()
    await expect(row(page, 'checkout-flow', 'enter-card-details')).toHaveCSS('border-top-style', 'dashed')
  })

  test("Show a child's text when the pointer rests on it", async ({ page }) => {
    seedChild('confirm-order', 'Confirm order')
    writeInto(join(sessions, 'confirm-order', 'confirm-order.md'), '# Confirm order\n\nShow the order and take the payment.\n')
    await openWholeBoard(page)
    await row(page, 'checkout-flow', 'confirm-order').hover()
    await expect(row(page, 'checkout-flow', 'confirm-order')).toHaveAttribute('title', 'Show the order and take the payment.')
  })
})

test.describe('Expand Parent Ticket', () => {
  test.beforeEach(() => {
    seedChild('enter-card-details', 'Enter card details')
    seedChild('confirm-order', 'Confirm order')
  })

  test('Expand a parent to show its children', async ({ page }) => {
    await openWholeBoard(page)
    await childrenLine(page, 'checkout-flow').click()
    await expect(childrenLine(page, 'checkout-flow')).toHaveText('+ 2 children')
    await childrenLine(page, 'checkout-flow').click()
    await expect(rowsOf(page, 'checkout-flow')).toHaveCount(2)
    await expect(childrenLine(page, 'checkout-flow')).toHaveText('- 2 children')
  })

  test('Collapse a parent to its own card', async ({ page }) => {
    await openWholeBoard(page)
    await expect(rowsOf(page, 'checkout-flow')).toHaveCount(2)
    await childrenLine(page, 'checkout-flow').click()
    await expect(rowsOf(page, 'checkout-flow')).toHaveCount(0)
    await expect(childrenLine(page, 'checkout-flow')).toHaveText('+ 2 children')
  })
})

test.describe('Detach Child Ticket', () => {
  test('Pull a child out of its parent', async ({ page }) => {
    seedChild('enter-card-details', 'Enter card details')
    await openWholeBoard(page)
    await dragCard(page, row(page, 'checkout-flow', 'enter-card-details'), listOf(page, 'Discovery'), BY_ITS_ROW)
    await expect(cardIn(page, 'Discovery', 'enter-card-details').locator(':scope > .ticket-title-line .ticket-title')).toHaveText('Checkout flow.Enter card details', { timeout: 10_000 })
    expect(sessionJson('enter-card-details')).toMatchObject({ parent: 'checkout-flow', pulled_out: true })
    await expect(row(page, 'checkout-flow', 'enter-card-details')).toHaveCSS('border-top-style', 'dashed')
  })

  test('Move a pulled-out child like any ticket', async ({ page }) => {
    seedChild('enter-card-details', 'Enter card details', { pulledOut: true, log: [DONE_IN_DISCOVERY] })
    await openWholeBoard(page)
    const specification = listOf(page, 'Specification')
    await specification.scrollIntoViewIfNeeded()
    await dragCard(page, card(page, 'enter-card-details'), specification)
    await expect(cardIn(page, 'Specification', 'enter-card-details')).toBeVisible({ timeout: 10_000 })
    expect(sessionJson('enter-card-details').parent).toBe('checkout-flow')
  })
})

test.describe('Reassign Ticket Parent', () => {
  test('Move a child to another parent', async ({ page }) => {
    seedChild('enter-card-details', 'Enter card details')
    await openWholeBoard(page)
    await dragCard(page, row(page, 'checkout-flow', 'enter-card-details'), card(page, 'billing-report'), BY_ITS_ROW)
    await expect(row(page, 'billing-report', 'enter-card-details')).toBeVisible({ timeout: 10_000 })
    await expect(row(page, 'checkout-flow', 'enter-card-details')).toHaveCount(0)
    await expect.poll(() => sessionJson('enter-card-details').parent).toBe('billing-report')
  })

  test('Take a child off its parent', async ({ page }) => {
    seedChild('enter-card-details', 'Enter card details')
    await openWholeBoard(page)
    await page.keyboard.down('Alt')
    await dragCard(page, row(page, 'checkout-flow', 'enter-card-details'), listOf(page, 'Discovery'), BY_ITS_ROW)
    await page.keyboard.up('Alt')
    await expect(card(page, 'enter-card-details').locator(':scope > .ticket-title-line .ticket-title')).toHaveText('Enter card details', { timeout: 10_000 })
    await expect(row(page, 'checkout-flow', 'enter-card-details')).toHaveCount(0)
    await expect.poll(() => sessionJson('enter-card-details').parent ?? '').toBe('')
  })

  test('Start a Backlog item under a ticket', async ({ page }) => {
    await openWholeBoard(page)
    await dragCard(page, page.locator('.ticket-card[data-item="Search the catalog"]'), card(page, 'checkout-flow'))
    await expect(row(page, 'checkout-flow', 'search-the-catalog')).toBeVisible({ timeout: 10_000 })
    await expect(toast(page, 'Search the catalog started as a child of checkout-flow')).toBeVisible()
  })

  test('Refuse to make a ticket a child of its own child', async ({ page }) => {
    seedChild('enter-card-details', 'Enter card details')
    await openWholeBoard(page)
    const childRow = row(page, 'checkout-flow', 'enter-card-details')
    await holdOver(page, card(page, 'checkout-flow'), childRow)
    await expect(childRow).not.toHaveClass(/is-drop-over/)
    await page.mouse.up()
    await expect(row(page, 'checkout-flow', 'enter-card-details')).toBeVisible()
    expect(sessionJson('checkout-flow').parent ?? '').toBe('')
  })
})

test.describe('Place Parent At Leftmost Child Stage', () => {
  test("Show a parent in its earliest child's stage", async ({ page }) => {
    seedChild('enter-card-details', 'Enter card details', { log: [IN_SPECIFICATION] })
    seedChild('confirm-order', 'Confirm order')
    await openWholeBoard(page)
    await expect(cardIn(page, 'Discovery', 'checkout-flow')).toBeVisible()
  })

  // A child stacked in its parent's card leaves it when dragged onto a column, so confirm-order is a card of its own
  // here, pulled out, and moves on as any ticket does.
  test('Move a parent on when its last child moves on', async ({ page }) => {
    seedChild('enter-card-details', 'Enter card details', { log: [IN_SPECIFICATION] })
    seedChild('confirm-order', 'Confirm order', { pulledOut: true, log: [DONE_IN_DISCOVERY] })
    await openWholeBoard(page)
    await expect(cardIn(page, 'Discovery', 'checkout-flow')).toBeVisible()
    const specification = listOf(page, 'Specification')
    await specification.scrollIntoViewIfNeeded()
    await dragCard(page, card(page, 'confirm-order'), specification)
    await expect(cardIn(page, 'Specification', 'checkout-flow')).toBeVisible({ timeout: 10_000 })
  })

  test('Refuse to move a parent by hand', async ({ page }) => {
    seedChild('confirm-order', 'Confirm order')
    await openWholeBoard(page)
    const specification = listOf(page, 'Specification')
    await specification.scrollIntoViewIfNeeded()
    await dragCard(page, card(page, 'checkout-flow'), specification)
    await expect(toast(page, 'checkout-flow has child tickets; a parent moves only with its children').first()).toBeVisible({ timeout: 10_000 })
    await expect(cardIn(page, 'Discovery', 'checkout-flow')).toBeVisible()
  })
})
