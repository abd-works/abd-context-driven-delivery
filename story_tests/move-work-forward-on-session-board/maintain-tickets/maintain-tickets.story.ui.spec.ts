/**
 * Maintain Tickets at the browser tier: what a person does on the board page to keep a ticket up to date.
 *
 * Scenarios: story_tests/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md,
 * the stories Edit Ticket Text, Reorder Tickets In Column, Delete Ticket, and Tag Ticket Session. The Python tiers
 * replay them from maintain-tickets.story.shared.py; here each scenario is one test, done on the page.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/`, where the board reads it, and opens the board; a When does what the person does on the page; a Then
 * reads what the person sees, and the file the board keeps it in. Each step runs through `step`, which screenshots the
 * settled page and writes the step's row to the run's results.json (space/kanban/app/tests/step-capture.ts).
 */
import { existsSync, readFileSync, rmSync } from 'node:fs'
import { join } from 'node:path'

import { card, dragCard, expect, fixtureRoot, openWholeBoard, openCardOf, readBoardAgain, resetSessions, step, test, toast, writeInto, writeSession } from '../../../space/kanban/app/tests/story-ui'
import type { Locator, Page } from '../../../space/kanban/app/tests/story-ui'

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
    await step(page, "Given the ticket checkout-flow's session folder holds checkout-flow.md with the text Pay for the basket.", () => {
      writeInto(sessionFile('checkout-flow', 'checkout-flow.md'), '# Checkout flow\n\nPay for the basket.\n')
    })
    await step(page, 'When the Person opens the board', async () => {
      await openWholeBoard(page)
      await expect(closedText(page, 'checkout-flow')).toHaveCount(0)
      await openCardOf(page, 'checkout-flow')
    })
    await step(page, "Then checkout-flow's card shows Pay for the basket.", async () => {
      await expect(shownText(page, 'checkout-flow')).toHaveText('Pay for the basket.')
    })
  })

  test("Show only the opening of a ticket's text, with a link to its file", async ({ page }) => {
    let opened: Locator
    await step(page, "Given checkout-flow's text is three paragraphs: Pay for the basket, Take the card, Send the receipt", async () => {
      writeInto(sessionFile('checkout-flow', 'checkout-flow.md'), '# Checkout flow\n\nPay for the basket.\n\nTake the card.\n\nSend the receipt.\n')
      await openWholeBoard(page)
    })
    await step(page, "When the Person opens checkout-flow's card", async () => {
      opened = await openCardOf(page, 'checkout-flow')
    })
    await step(page, 'Then the card shows only Pay for the basket and Take the card', async () => {
      await expect(shownText(page, 'checkout-flow')).toHaveText('Pay for the basket.\n\nTake the card.')
    })
    await step(page, 'When the Person follows More in checkout-flow.md', async () => {
      await opened.getByRole('button', { name: 'More in checkout-flow.md' }).click()
    })
    await step(page, 'Then the files panel shows the whole text, Send the receipt included', async () => {
      await expect(page.locator('[data-panel="files"]')).toContainText('Send the receipt.')
    })
  })

  test("Edit a ticket's text", async ({ page }) => {
    await step(page, "Given the ticket checkout-flow's card shows Pay for the basket.", async () => {
      writeInto(sessionFile('checkout-flow', 'checkout-flow.md'), '# Checkout flow\n\nPay for the basket.\n')
      await openWholeBoard(page)
      await openCardOf(page, 'checkout-flow')
      await expect(shownText(page, 'checkout-flow')).toHaveText('Pay for the basket.')
    })
    await step(page, "When the Person edits checkout-flow's text to Pay for the basket by card.", async () => {
      await writeInField(page, await openCardOf(page, 'checkout-flow'), 'Edit text', 'Ticket text', 'Pay for the basket by card.')
    })
    await step(page, "Then checkout-flow.md in checkout-flow's session folder holds Pay for the basket by card.", async () => {
      await expect.poll(() => textOf(sessionFile('checkout-flow', 'checkout-flow.md'))).toContain('Pay for the basket by card.')
    })
    await step(page, "And checkout-flow's card shows Pay for the basket by card.", async () => {
      await expect(shownText(page, 'checkout-flow')).toHaveText('Pay for the basket by card.')
    })
  })

  test('Write the text file for a ticket that has none', async ({ page }) => {
    await step(page, 'Given the ticket pet-visits is on the board', async () => {
      writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
      await openWholeBoard(page)
    })
    await step(page, "But pet-visits' session folder holds no pet-visits.md", () => {
      expect(existsSync(sessionFile('pet-visits', 'pet-visits.md'))).toBe(false)
    })
    await step(page, "When the Person edits pet-visits' text to Book a visit for a pet.", async () => {
      await writeInField(page, await openCardOf(page, 'pet-visits'), 'Edit text', 'Ticket text', 'Book a visit for a pet.')
    })
    await step(page, "Then pet-visits.md in pet-visits' session folder holds Book a visit for a pet.", async () => {
      await expect.poll(() => textOf(sessionFile('pet-visits', 'pet-visits.md'))).toContain('Book a visit for a pet.')
    })
    await step(page, "And pet-visits' card shows Book a visit for a pet.", async () => {
      await expect(shownText(page, 'pet-visits')).toHaveText('Book a visit for a pet.')
    })
  })

  test("Edit a backlog item's text", async ({ page }) => {
    await step(page, 'Given the backlog item Gift cards has the text Sell gift cards.', async () => {
      writeInto(backlogFile('gift-cards'), '# Gift cards\n\nSell gift cards.\n')
      await openWholeBoard(page)
      await expect(backlogCard(page, 'Gift cards').locator('.ticket-text')).toHaveCount(0)
      await backlogCard(page, 'Gift cards').getByRole('button', { name: 'Show Gift cards' }).click()
      await expect(backlogCard(page, 'Gift cards').locator('.ticket-text')).toHaveText('Sell gift cards.')
    })
    await step(page, "When the Person edits Gift cards' text to Sell gift cards at the till.", async () => {
      await writeInField(page, backlogCard(page, 'Gift cards'), 'Edit text', 'Item text', 'Sell gift cards at the till.')
    })
    await step(page, "Then Gift cards' file, .sessions/_backlog/gift-cards.md, holds Sell gift cards at the till.", async () => {
      await expect.poll(() => textOf(backlogFile('gift-cards'))).toContain('Sell gift cards at the till.')
    })
    await step(page, 'And the Backlog shows Gift cards with the text Sell gift cards at the till.', async () => {
      await expect(backlogCard(page, 'Gift cards').locator('.ticket-text')).toHaveText('Sell gift cards at the till.')
    })
  })

  test("Edit a child's text inside its parent", async ({ page }) => {
    const row = card(page, 'checkout-flow').locator('[data-child="confirm-order"]').first()
    await step(page, 'Given the ticket checkout-flow holds its child ticket confirm-order', async () => {
      writeSession(fixtureRoot, { name: 'confirm-order', title: 'Confirm order', parent: 'checkout-flow' })
      writeInto(sessionFile('confirm-order', 'confirm-order.md'), '# Confirm order\n\nShow the order and take the payment.\n')
      await openWholeBoard(page)
    })
    await step(page, "And confirm-order's text is Show the order and take the payment.", async () => {
      await expect(row).toHaveAttribute('title', 'Show the order and take the payment.')
    })
    await step(page, "When the Person edits confirm-order's text inside checkout-flow's card to Show the order, then take the payment.", async () => {
      await writeInField(page, row, 'Edit text', 'Ticket text', 'Show the order, then take the payment.')
    })
    await step(page, "Then confirm-order.md in confirm-order's session folder holds Show the order, then take the payment.", async () => {
      await expect.poll(() => textOf(sessionFile('confirm-order', 'confirm-order.md'))).toContain('Show the order, then take the payment.')
    })
    await step(page, "And opening confirm-order from checkout-flow's card shows Show the order, then take the payment.", async () => {
      await row.getByRole('button', { name: 'Edit text' }).first().click()
      const editor = page.getByRole('textbox', { name: 'Ticket text' })
      await expect(editor).toHaveValue('Show the order, then take the payment.')
      expect(await editor.evaluate(box => box.scrollWidth <= box.clientWidth && box.scrollHeight <= box.clientHeight)).toBe(true)
    })
  })
})

test.describe('Reorder Tickets In Column', () => {
  test('Keep a ticket where it was moved in its column', async ({ page }) => {
    const names = ['pet-visits', 'sign-up']
    await step(page, 'Given the Discovery column shows the ticket pet-visits above sign-up', async () => {
      writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
      writeSession(fixtureRoot, { name: 'sign-up', title: 'Sign up' })
      await openWholeBoard(page)
      await expect.poll(() => orderOf(inProgressOf(page, 'Discovery'), names)).toEqual(names)
    })
    await step(page, 'When the Person moves sign-up above pet-visits in Discovery', async () => {
      await dragCard(page, card(page, 'sign-up'), card(page, 'pet-visits'), { onTop: true })
    })
    await step(page, 'Then Discovery shows sign-up above pet-visits', async () => {
      await expect.poll(() => orderOf(inProgressOf(page, 'Discovery'), names)).toEqual(['sign-up', 'pet-visits'])
    })
    await step(page, 'And Discovery still shows sign-up above pet-visits when the board is read again', async () => {
      await readBoardAgain(page)
      await expect.poll(() => orderOf(inProgressOf(page, 'Discovery'), names)).toEqual(['sign-up', 'pet-visits'])
    })
  })

  test('Keep a backlog item where it was moved', async ({ page }) => {
    const titles = ['Gift cards', 'Returns and refunds']
    await step(page, 'Given the Backlog shows the backlog item Gift cards above Returns and refunds', async () => {
      writeInto(backlogFile('gift-cards'), '# Gift cards\n\nSell gift cards.\n')
      writeInto(backlogFile('returns-and-refunds'), '# Returns and refunds\n\nTake goods back.\n')
      await openWholeBoard(page)
      await expect.poll(() => itemOrderOf(page, titles)).toEqual(titles)
    })
    await step(page, 'When the Person moves Returns and refunds above Gift cards', async () => {
      await dragCard(page, backlogCard(page, 'Returns and refunds'), backlogCard(page, 'Gift cards'), { onTop: true })
    })
    await step(page, 'Then the Backlog shows Returns and refunds above Gift cards', async () => {
      await expect.poll(() => itemOrderOf(page, titles)).toEqual(['Returns and refunds', 'Gift cards'])
    })
    await step(page, 'And the Backlog still shows Returns and refunds above Gift cards when the board is read again', async () => {
      await readBoardAgain(page)
      await expect.poll(() => itemOrderOf(page, titles)).toEqual(['Returns and refunds', 'Gift cards'])
    })
  })

  test('Keep a backlog item below the one it was dropped on', async ({ page }) => {
    const titles = ['Gift cards', 'Returns and refunds']
    await step(page, 'Given the Backlog shows the backlog item Gift cards above Returns and refunds', async () => {
      writeInto(backlogFile('gift-cards'), '# Gift cards\n\nSell gift cards.\n')
      writeInto(backlogFile('returns-and-refunds'), '# Returns and refunds\n\nTake goods back.\n')
      await openWholeBoard(page)
      await expect.poll(() => itemOrderOf(page, titles)).toEqual(titles)
    })
    await step(page, 'When the Person drops Gift cards on the bottom of Returns and refunds', async () => {
      await dragCard(page, backlogCard(page, 'Gift cards'), backlogCard(page, 'Returns and refunds'), { onBottom: true })
    })
    await step(page, 'Then the Backlog shows Gift cards below Returns and refunds', async () => {
      await expect.poll(() => itemOrderOf(page, titles)).toEqual(['Returns and refunds', 'Gift cards'])
    })
  })
})

test.describe('Nest Backlog Items', () => {
  const childRow = (page: Page, parent: string, child: string) => backlogCard(page, parent).locator(`[data-child-item="${child}"]`)

  test('Make a backlog item the child of the one it was dropped in the middle of', async ({ page }) => {
    await step(page, 'Given the Backlog shows the backlog items Gift cards and Returns and refunds', async () => {
      writeInto(backlogFile('gift-cards'), '# Gift cards\n\nSell gift cards.\n')
      writeInto(backlogFile('returns-and-refunds'), '# Returns and refunds\n\nTake goods back.\n')
      await openWholeBoard(page)
    })
    await step(page, 'When the Person drops Returns and refunds in the middle of Gift cards', async () => {
      await dragCard(page, backlogCard(page, 'Returns and refunds'), backlogCard(page, 'Gift cards'))
    })
    await step(page, 'Then Gift cards shows Returns and refunds as its child', async () => {
      await expect(childRow(page, 'Gift cards', 'Returns and refunds')).toBeVisible()
    })
    await step(page, 'And the Backlog no longer shows Returns and refunds as an item of its own', async () => {
      await expect(backlogCard(page, 'Returns and refunds')).toHaveCount(0)
    })
    await step(page, "And Returns and refunds' file is in the Gift cards folder", async () => {
      await expect.poll(() => existsSync(join(sessions, '_backlog', 'gift-cards', 'returns-and-refunds.md'))).toBe(true)
    })
  })

  test('Take a child out of its parent onto the Backlog', async ({ page }) => {
    await step(page, 'Given the backlog item Gift cards holds its child Returns and refunds', async () => {
      writeInto(join(sessions, '_backlog', 'gift-cards', 'gift-cards.md'), '# Gift cards\n\nSell gift cards.\n')
      writeInto(join(sessions, '_backlog', 'gift-cards', 'returns-and-refunds.md'), '# Returns and refunds\n\nTake goods back.\n')
      await openWholeBoard(page)
      await expect(childRow(page, 'Gift cards', 'Returns and refunds')).toBeVisible()
    })
    await step(page, 'When the Person drags Returns and refunds out of Gift cards onto the Backlog', async () => {
      await dragCard(page, childRow(page, 'Gift cards', 'Returns and refunds'), page.locator('.board-column[data-column="Backlog"] .card-list').first())
    })
    await step(page, 'Then the Backlog shows Returns and refunds as an item of its own', async () => {
      await expect(backlogCard(page, 'Returns and refunds')).toBeVisible()
    })
    await step(page, "And Returns and refunds' file is back in .sessions/_backlog", async () => {
      await expect.poll(() => existsSync(backlogFile('returns-and-refunds'))).toBe(true)
    })
  })
})

test.describe('Delete Ticket', () => {
  test('Delete a ticket and its session folder', async ({ page }) => {
    await step(page, 'Given the ticket pet-visits is on the board', async () => {
      writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
      await openWholeBoard(page)
    })
    await step(page, 'When the Person deletes pet-visits', async () => {
      const opened = await openCardOf(page, 'pet-visits')
      page.once('dialog', dialog => void dialog.accept())
      await opened.getByRole('button', { name: 'Delete' }).click()
    })
    await step(page, 'Then no column shows pet-visits', async () => {
      await expect(card(page, 'pet-visits')).toHaveCount(0)
    })
    await step(page, 'And .sessions/pet-visits is gone', async () => {
      await expect.poll(() => existsSync(join(sessions, 'pet-visits'))).toBe(false)
    })
  })

  // The board shows a ticket another chat has just deleted until it reads the board again; the page's own reads are held
  // still, so Delete is pressed on a ticket the board no longer has.
  test('Refuse to delete a ticket the board does not have', async ({ page }) => {
    let opened: Locator
    await step(page, "Given the board still shows no-such-ticket's card, but its session folder is gone", async () => {
      writeSession(fixtureRoot, { name: 'no-such-ticket', title: 'No such ticket' })
      await page.clock.install()
      await openWholeBoard(page)
      opened = await openCardOf(page, 'no-such-ticket')
      rmSync(join(sessions, 'no-such-ticket'), { recursive: true, force: true })
    })
    await step(page, 'When the Person deletes no-such-ticket', async () => {
      page.once('dialog', dialog => void dialog.accept())
      await opened.getByRole('button', { name: 'Delete' }).click()
    })
    await step(page, "Then the board says no ticket named 'no-such-ticket' on the board", async () => {
      await expect(toast(page, "no ticket named 'no-such-ticket' on the board").first()).toBeVisible()
    })
    await step(page, "And deleting no-such-ticket removes no other ticket's session folder", () => {
      expect([existsSync(join(sessions, 'checkout-flow')), existsSync(join(sessions, 'billing-report'))]).toEqual([true, true])
    })
  })
})

test.describe('Tag Ticket Session', () => {
  const tagsOf = (page: Page, ticket: string) => card(page, ticket).locator(':scope > .ticket-tags .ticket-tag')

  test("Tag a ticket's session", async ({ page }) => {
    await step(page, 'Given the ticket pet-visits has no tags', async () => {
      writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
      await openWholeBoard(page)
    })
    await step(page, "When the Person tags pet-visits' session with billing", async () => {
      await writeInField(page, await openCardOf(page, 'pet-visits'), 'Tag', 'Tag', 'billing')
    })
    await step(page, "Then pet-visits' card shows the tag billing", async () => {
      await expect(tagsOf(page, 'pet-visits')).toHaveText(['billing'])
    })
    await step(page, "And pet-visits' session.json holds the tag billing", () => {
      expect(sessionJson('pet-visits').tags).toEqual(['billing'])
    })
  })

  test('Add a second tag', async ({ page }) => {
    await step(page, 'Given the ticket pet-visits is tagged billing', async () => {
      writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits', tags: ['billing'] })
      await openWholeBoard(page)
      await expect(tagsOf(page, 'pet-visits')).toHaveText(['billing'])
    })
    await step(page, "When the Person tags pet-visits' session with urgent", async () => {
      await writeInField(page, await openCardOf(page, 'pet-visits'), 'Tag', 'Tag', 'urgent')
    })
    await step(page, "Then pet-visits' card shows the tags billing and urgent", async () => {
      await expect(tagsOf(page, 'pet-visits')).toHaveText(['billing', 'urgent'])
    })
  })
})
