/**
 * Maintain Tickets at the browser tier: what a person does on the board page to keep a ticket up to date.
 *
 * Scenarios: harness/.context/stories/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md,
 * the stories Edit Ticket Text, Reorder Tickets In Column, Delete Ticket, and Tag Ticket Session. The Python tiers
 * replay them from maintain-tickets.story.shared.py; here each scenario is one test, done on the page.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/`, where the board reads it; a When does what the person does on the page; a Then reads what the person
 * sees, and the file the board keeps it in.
 */
import { existsSync, readFileSync, rmSync } from 'node:fs'
import { join } from 'node:path'

import { card, dragCard, expect, fixtureRoot, openWholeBoard, openCardOf, resetSessions, test, toast, writeInto, writeSession } from './app/tests/story-ui'
import type { Locator, Page } from './app/tests/story-ui'

const sessions = join(fixtureRoot, '.sessions')
const sessionFile = (ticket: string, file: string) => join(sessions, ticket, file)
const sessionJson = (ticket: string): { tags?: string[] } => JSON.parse(readFileSync(sessionFile(ticket, 'session.json'), 'utf-8'))
const textOf = (path: string) => (existsSync(path) ? readFileSync(path, 'utf-8') : '')
const backlogCard = (page: Page, title: string) => page.locator(`.ticket-card[data-item="${title}"]`)
const backlogFile = (slug: string) => join(sessions, '_backlog', `${slug}.md`)
const inProgressOf = (page: Page, column: string) => page.locator(`.board-column[data-column="${column}"] .card-list`).first()

// The text shown under a ticket's title: only its open card shows it, cut to its opening paragraphs.
const shownText = (page: Page, ticket: string) => page.locator(`[data-open-card="${ticket}"] > .ticket-text`)
const closedText = (page: Page, ticket: string) => card(page, ticket).locator(':scope > .ticket-text')

async function writeInField(page: Page, opened: Locator, control: string, field: string, typed: string): Promise<void> {
  await opened.getByRole('button', { name: control }).first().click()
  const input = page.getByRole('textbox', { name: field })
  await input.fill(typed)
  await input.press('Enter')
}

// The order a list shows these tickets in, top to bottom.
const orderOf = (list: Locator, names: string[]) => list.locator('[data-ticket]').evaluateAll((cards, wanted) => cards.map(shown => shown.getAttribute('data-ticket')).filter(name => wanted.includes(name ?? '')), names)
const itemOrderOf = (page: Page, titles: string[]) => page.locator('.board-column[data-column="Backlog"] [data-item]').evaluateAll((cards, wanted) => cards.map(shown => shown.getAttribute('data-item')).filter(title => wanted.includes(title ?? '')), titles)

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('Edit Ticket Text', () => {
  test("Show a ticket's text from its session file", async ({ page }) => {
    writeInto(sessionFile('checkout-flow', 'checkout-flow.md'), '# Checkout flow\n\nPay for the basket.\n')
    await openWholeBoard(page)
    await expect(closedText(page, 'checkout-flow')).toHaveCount(0)
    await openCardOf(page, 'checkout-flow')
    await expect(shownText(page, 'checkout-flow')).toHaveText('Pay for the basket.')
  })

  test("Show only the opening of a ticket's text, with a link to its file", async ({ page }) => {
    writeInto(sessionFile('checkout-flow', 'checkout-flow.md'), '# Checkout flow\n\nPay for the basket.\n\nTake the card.\n\nSend the receipt.\n')
    await openWholeBoard(page)
    const opened = await openCardOf(page, 'checkout-flow')
    await expect(shownText(page, 'checkout-flow')).toHaveText('Pay for the basket.\n\nTake the card.')
    await opened.getByRole('button', { name: 'More in checkout-flow.md' }).click()
    await expect(page.locator('[data-panel="files"]')).toContainText('Send the receipt.')
  })

  test("Edit a ticket's text", async ({ page }) => {
    writeInto(sessionFile('checkout-flow', 'checkout-flow.md'), '# Checkout flow\n\nPay for the basket.\n')
    await openWholeBoard(page)
    await openCardOf(page, 'checkout-flow')
    await expect(shownText(page, 'checkout-flow')).toHaveText('Pay for the basket.')
    await writeInField(page, await openCardOf(page, 'checkout-flow'), 'Edit text', 'Ticket text', 'Pay for the basket by card.')
    await expect(shownText(page, 'checkout-flow')).toHaveText('Pay for the basket by card.')
    await expect.poll(() => textOf(sessionFile('checkout-flow', 'checkout-flow.md'))).toContain('Pay for the basket by card.')
  })

  test('Write the text file for a ticket that has none', async ({ page }) => {
    writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
    await openWholeBoard(page)
    expect(existsSync(sessionFile('pet-visits', 'pet-visits.md'))).toBe(false)
    await writeInField(page, await openCardOf(page, 'pet-visits'), 'Edit text', 'Ticket text', 'Book a visit for a pet.')
    await expect(shownText(page, 'pet-visits')).toHaveText('Book a visit for a pet.')
    await expect.poll(() => textOf(sessionFile('pet-visits', 'pet-visits.md'))).toContain('Book a visit for a pet.')
  })

  test("Edit a backlog item's text", async ({ page }) => {
    writeInto(backlogFile('gift-cards'), '# Gift cards\n\nSell gift cards.\n')
    await openWholeBoard(page)
    await expect(backlogCard(page, 'Gift cards').locator('.ticket-text')).toHaveCount(0)
    await backlogCard(page, 'Gift cards').getByRole('button', { name: 'Show Gift cards' }).click()
    await expect(backlogCard(page, 'Gift cards').locator('.ticket-text')).toHaveText('Sell gift cards.')
    await writeInField(page, backlogCard(page, 'Gift cards'), 'Edit text', 'Item text', 'Sell gift cards at the till.')
    await expect(backlogCard(page, 'Gift cards').locator('.ticket-text')).toHaveText('Sell gift cards at the till.')
    await expect.poll(() => textOf(backlogFile('gift-cards'))).toContain('Sell gift cards at the till.')
  })

  test("Edit a child's text inside its parent", async ({ page }) => {
    writeSession(fixtureRoot, { name: 'confirm-order', title: 'Confirm order', parent: 'checkout-flow' })
    writeInto(sessionFile('confirm-order', 'confirm-order.md'), '# Confirm order\n\nShow the order and take the payment.\n')
    await openWholeBoard(page)
    const row = card(page, 'checkout-flow').locator('[data-child="confirm-order"]').first()
    await expect(row).toHaveAttribute('title', 'Show the order and take the payment.')
    await writeInField(page, row, 'Edit text', 'Ticket text', 'Show the order, then take the payment.')
    await expect(row).toHaveAttribute('title', 'Show the order, then take the payment.')
    expect(textOf(sessionFile('confirm-order', 'confirm-order.md'))).toContain('Show the order, then take the payment.')
  })
})

test.describe('Reorder Tickets In Column', () => {
  test('Keep a ticket where it was moved in its column', async ({ page }) => {
    writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
    writeSession(fixtureRoot, { name: 'sign-up', title: 'Sign up' })
    await openWholeBoard(page)
    const discovery = inProgressOf(page, 'Discovery')
    await expect.poll(() => orderOf(discovery, ['pet-visits', 'sign-up'])).toEqual(['pet-visits', 'sign-up'])
    await dragCard(page, card(page, 'sign-up'), card(page, 'pet-visits'), { onTop: true })
    await expect.poll(() => orderOf(discovery, ['pet-visits', 'sign-up'])).toEqual(['sign-up', 'pet-visits'])
    await page.reload()
    await expect.poll(() => orderOf(inProgressOf(page, 'Discovery'), ['pet-visits', 'sign-up'])).toEqual(['sign-up', 'pet-visits'])
  })

  test('Keep a backlog item where it was moved', async ({ page }) => {
    writeInto(backlogFile('gift-cards'), '# Gift cards\n\nSell gift cards.\n')
    writeInto(backlogFile('returns-and-refunds'), '# Returns and refunds\n\nTake goods back.\n')
    await openWholeBoard(page)
    const titles = ['Gift cards', 'Returns and refunds']
    await expect.poll(() => itemOrderOf(page, titles)).toEqual(titles)
    await dragCard(page, backlogCard(page, 'Returns and refunds'), backlogCard(page, 'Gift cards'), { onTop: true })
    await expect.poll(() => itemOrderOf(page, titles)).toEqual(['Returns and refunds', 'Gift cards'])
    await page.reload()
    await expect.poll(() => itemOrderOf(page, titles)).toEqual(['Returns and refunds', 'Gift cards'])
  })

  test('Keep a backlog item below the one it was dropped on', async ({ page }) => {
    writeInto(backlogFile('gift-cards'), '# Gift cards\n\nSell gift cards.\n')
    writeInto(backlogFile('returns-and-refunds'), '# Returns and refunds\n\nTake goods back.\n')
    await openWholeBoard(page)
    const titles = ['Gift cards', 'Returns and refunds']
    await expect.poll(() => itemOrderOf(page, titles)).toEqual(titles)
    await dragCard(page, backlogCard(page, 'Gift cards'), backlogCard(page, 'Returns and refunds'), { onBottom: true })
    await expect.poll(() => itemOrderOf(page, titles)).toEqual(['Returns and refunds', 'Gift cards'])
  })
})

test.describe('Nest Backlog Items', () => {
  const childRow = (page: Page, parent: string, child: string) => backlogCard(page, parent).locator(`[data-child-item="${child}"]`)

  test('Make a backlog item the child of the one it was dropped in the middle of', async ({ page }) => {
    writeInto(backlogFile('gift-cards'), '# Gift cards\n\nSell gift cards.\n')
    writeInto(backlogFile('returns-and-refunds'), '# Returns and refunds\n\nTake goods back.\n')
    await openWholeBoard(page)
    await dragCard(page, backlogCard(page, 'Returns and refunds'), backlogCard(page, 'Gift cards'))
    await expect(childRow(page, 'Gift cards', 'Returns and refunds')).toBeVisible()
    await expect(backlogCard(page, 'Returns and refunds')).toHaveCount(0)
    await expect.poll(() => existsSync(join(sessions, '_backlog', 'gift-cards', 'returns-and-refunds.md'))).toBe(true)
  })

  test('Take a child out of its parent onto the Backlog', async ({ page }) => {
    writeInto(join(sessions, '_backlog', 'gift-cards', 'gift-cards.md'), '# Gift cards\n\nSell gift cards.\n')
    writeInto(join(sessions, '_backlog', 'gift-cards', 'returns-and-refunds.md'), '# Returns and refunds\n\nTake goods back.\n')
    await openWholeBoard(page)
    await expect(childRow(page, 'Gift cards', 'Returns and refunds')).toBeVisible()
    await dragCard(page, childRow(page, 'Gift cards', 'Returns and refunds'), page.locator('.board-column[data-column="Backlog"] .card-list').first())
    await expect(backlogCard(page, 'Returns and refunds')).toBeVisible()
    await expect.poll(() => existsSync(backlogFile('returns-and-refunds'))).toBe(true)
  })
})

test.describe('Delete Ticket', () => {
  test('Delete a ticket and its session folder', async ({ page }) => {
    writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
    await openWholeBoard(page)
    const opened = await openCardOf(page, 'pet-visits')
    page.once('dialog', dialog => void dialog.accept())
    await opened.getByRole('button', { name: 'Delete' }).click()
    await expect(card(page, 'pet-visits')).toHaveCount(0)
    await expect.poll(() => existsSync(join(sessions, 'pet-visits'))).toBe(false)
  })

  // The board shows a ticket another chat has just deleted until it reads the board again; the page's own reads are held
  // still, so Delete is pressed on a ticket the board no longer has.
  test('Refuse to delete a ticket the board does not have', async ({ page }) => {
    writeSession(fixtureRoot, { name: 'no-such-ticket', title: 'No such ticket' })
    await page.clock.install()
    await openWholeBoard(page)
    const opened = await openCardOf(page, 'no-such-ticket')
    rmSync(join(sessions, 'no-such-ticket'), { recursive: true, force: true })
    page.once('dialog', dialog => void dialog.accept())
    await opened.getByRole('button', { name: 'Delete' }).click()
    await expect(toast(page, "no ticket named 'no-such-ticket' on the board").first()).toBeVisible()
    expect([existsSync(join(sessions, 'checkout-flow')), existsSync(join(sessions, 'billing-report'))]).toEqual([true, true])
  })
})

test.describe('Tag Ticket Session', () => {
  test("Tag a ticket's session", async ({ page }) => {
    writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
    await openWholeBoard(page)
    await writeInField(page, await openCardOf(page, 'pet-visits'), 'Tag', 'Tag', 'billing')
    await expect(card(page, 'pet-visits').locator(':scope > .ticket-tags .ticket-tag')).toHaveText(['billing'])
    expect(sessionJson('pet-visits').tags).toEqual(['billing'])
  })

  test('Add a second tag', async ({ page }) => {
    writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits', tags: ['billing'] })
    await openWholeBoard(page)
    await expect(card(page, 'pet-visits').locator(':scope > .ticket-tags .ticket-tag')).toHaveText(['billing'])
    await writeInField(page, await openCardOf(page, 'pet-visits'), 'Tag', 'Tag', 'urgent')
    await expect(card(page, 'pet-visits').locator(':scope > .ticket-tags .ticket-tag')).toHaveText(['billing', 'urgent'])
  })
})
