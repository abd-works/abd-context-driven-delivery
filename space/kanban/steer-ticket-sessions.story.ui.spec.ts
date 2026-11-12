/**
 * Steer Ticket Sessions at the browser tier: the scenarios, and the Thens of the Python tiers' scenarios, that only the
 * board app's page shows.
 *
 * Scenarios: harness/.context/stories/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md, harness/.context/stories/move-work-forward-on-session-board/maintain-tickets/maintain_tickets_story.test.md and harness/.context/stories/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md. The Python tiers replay the
 * rest from steer-ticket-sessions.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/` or its git checkout; a chat is `FakeChat`, which checks in through the board's server as the cdd-board
 * mod does. A dialog that would commit, push, or merge is read and then cancelled, because the fixture's checkout is
 * shared by every later spec.
 */
import { execFileSync } from 'node:child_process'
import { mkdirSync, rmSync } from 'node:fs'
import { join } from 'node:path'

import { card, dragCard, expect, FakeChat, fixtureRoot, openBoard, receivedBy, resetSessions, test, toast, waitForChat, waitForNoChat, writeInto } from './app/tests/story-ui'
import type { Page } from './app/tests/story-ui'

const CHAT_CHECKED_IN_MILLISECONDS = 10_000

const git = (...args: string[]): string => execFileSync('git', args, { cwd: fixtureRoot, encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] })
const column = (page: Page, name: string) => page.locator(`.board-column[data-column="${name}"]`)
const backlogCards = (page: Page) => column(page, 'Backlog').locator('[data-item]')

// The fixture's checkout on main with no branch of a ticket, as fixture-repo.ts commits it.
function checkOutMainAlone(): void {
  git('checkout', '-f', 'main')
  for (const branch of git('branch', '--format=%(refname:short)').split('\n').filter(name => name && name !== 'main')) git('branch', '-D', branch)
}


test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('with no chat connected', () => {
  test.describe('Add Backlog Item', () => {
    test.describe('Add an idea to the Backlog', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await page.getByRole('button', { name: 'New backlog ticket' }).click()
        await page.getByRole('textbox', { name: 'Title' }).fill('Gift cards')
        await page.getByRole('textbox', { name: 'Text' }).fill('Sell gift cards.')
        await page.getByRole('button', { name: 'Add', exact: true }).click()
      })

      test('Then Gift cards is selected and the form is closed', async ({ page }) => {
        await expect(page.locator('.details-title h2')).toHaveText('Gift cards')
        await expect(page.getByRole('textbox', { name: 'Title' })).toHaveCount(0)
      })

      test('And a toast says Gift cards added to Backlog', async ({ page }) => {
        await expect(toast(page, 'Gift cards added to Backlog')).toBeVisible()
      })
    })

    test.describe('Keep Add off with no title', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await page.getByRole('button', { name: 'New backlog ticket' }).click()
        await page.getByRole('textbox', { name: 'Text' }).fill('An idea with no title.')
      })

      test('Then Add stays off', async ({ page }) => {
        await expect(page.getByRole('button', { name: 'Add', exact: true })).toBeDisabled()
      })

      test('And no backlog item is written', async ({ page }) => {
        await expect(backlogCards(page)).toHaveCount(1)
      })
    })

    test.describe('Start a backlog item in a chosen folder', () => {
      test.beforeEach(async ({ page }) => {
        writeInto(join(fixtureRoot, '.sessions', '_backlog', 'gift-cards.md'), '# Gift cards\n\nSell gift cards.\n')
        for (const folder of ['src/billing', 'src/visits']) mkdirSync(join(fixtureRoot, folder), { recursive: true })
        await openBoard(page)
        await backlogCards(page).filter({ hasText: 'Gift cards' }).getByRole('button', { name: 'Show Gift cards' }).click({ position: { x: 4, y: 4 } })
        await page.locator('.details-bar').getByRole('button', { name: 'Start', exact: true }).click()
        const dialog = page.getByRole('dialog')
        await dialog.getByRole('listitem').filter({ hasText: 'src/' }).click()
        await dialog.getByRole('listitem').filter({ hasText: 'visits/' }).click()
        await dialog.getByRole('button', { name: 'Use src/visits' }).click()
      })

      test.afterEach(() => rmSync(join(fixtureRoot, 'src'), { recursive: true, force: true }))

      test("Then the roots dialog stays open on gift-cards so its practices' roots can be set", async ({ page }) => {
        await expect(page.getByRole('dialog').getByRole('heading', { name: 'Roots of Gift cards' })).toBeVisible({ timeout: 8_000 })
      })

      test('And a toast says Gift cards started in Discovery', async ({ page }) => {
        await expect(toast(page, 'Gift cards started in Discovery')).toBeVisible({ timeout: 8_000 })
      })
    })
  })

  test.describe('Open Ticket Session', () => {
    test.describe('Keep + Ticket off with no chat', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await waitForNoChat(page)
      })

      test('Then + Ticket is off', async ({ page }) => {
        await expect(page.getByRole('button', { name: '+ Ticket' })).toBeDisabled()
      })
    })
  })

  test.describe('Split Ticket Into Child Tickets', () => {
    test.describe('Keep Split off where nothing can take the prompt', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await waitForNoChat(page)
      })

      test('Then Split is off', async ({ page }) => {
        await expect(card(page, 'checkout-flow').getByRole('button', { name: 'Split' }).first()).toBeDisabled()
      })
    })
  })

  test.describe('Write Ticket Handoff', () => {
    test.describe('Keep Handoff off with no chat', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await waitForNoChat(page)
      })

      test('Then Handoff is off', async ({ page }) => {
        await expect(card(page, 'checkout-flow').getByRole('button', { name: 'Handoff' }).first()).toBeDisabled()
      })

      test('And the header says No chat connected: load the cdd-board mod in a chat to send commands', async ({ page }) => {
        await expect(page.locator('.chat-missing')).toHaveText('No chat connected: load the cdd-board mod in a chat to send commands')
      })
    })
  })

  test.describe('Move Ticket', () => {
    test.describe('Move a ticket into the Backlog with its work', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await dragCard(page, card(page, 'back-to-backlog'), column(page, 'Backlog').locator('.card-list').first())
      })

      test('Then the Backlog shows the backlog item Back to backlog and it is selected', async ({ page }) => {
        await expect(page.locator('.details-title h2')).toHaveText('Back to backlog', { timeout: 8_000 })
      })

      test('And a toast says Back to backlog moved to Backlog', async ({ page }) => {
        await expect(toast(page, 'Back to backlog moved to Backlog')).toBeVisible({ timeout: 8_000 })
      })
    })
  })

  test.describe('Activate Ticket', () => {
    // Activating opens the ticket in its own worktree in one press: no chat moves between folders, so there is nothing
    // to ask first.
    test.describe('Open a ticket in its own worktree', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await card(page, 'billing-report').getByRole('button', { name: 'Activate' }).first().click()
        // Activating makes a worktree in the background; the next scenario's reset must not start while it still runs.
        await expect(toast(page, /^Billing report is open in its worktree/)).toBeVisible({ timeout: 15_000 })
      })

      test('Then no dialog opens', async ({ page }) => {
        await expect(page.getByRole('dialog')).toHaveCount(0)
      })

      test('And a toast names the worktree of Billing report, where its chat can be opened', async ({ page }) => {
        await expect(toast(page, /^Billing report is open in its worktree .+ · open its chat from its card$/)).toBeVisible({ timeout: 8_000 })
      })
    })
  })

  test.describe('Close Active Session', () => {
    test.describe('Complete the active ticket with its work committed', () => {
      test.beforeEach(async ({ page }) => {
        checkOutMainAlone()
        git('checkout', '-b', 'checkout-flow')
        await openBoard(page)
        await dragCard(page, card(page, 'checkout-flow'), column(page, 'Complete').locator('.card-list').first())
      })

      test.afterEach(async ({ page }) => {
        await page.getByRole('dialog').getByRole('button', { name: 'Cancel' }).click()
        checkOutMainAlone()
      })

      test('Then a dialog headed Close session Checkout flow offers commit and push, none chosen', async ({ page }) => {
        const dialog = page.getByRole('dialog')
        await expect(dialog.getByRole('heading', { name: 'Close session Checkout flow' })).toBeVisible({ timeout: 8_000 })
        await expect(dialog.getByRole('checkbox', { name: 'Commit changes on checkout-flow' })).not.toBeChecked()
        await expect(dialog.getByRole('checkbox', { name: 'Push checkout-flow to origin' })).not.toBeChecked()
      })
    })
  })
})

test.describe('with a chat connected', () => {
  let chat: FakeChat

  test.beforeAll(async ({ playwright, baseURL }) => {
    chat = new FakeChat(await playwright.request.newContext({ baseURL }), 'steer-chat', 'Steer chat')
    await chat.start()
  })

  test.afterAll(() => chat.stop())

  test.beforeEach(async ({ page }) => {
    chat.isBusy = false
    await openBoard(page)
    await waitForChat(page, chat)
  })

  test.describe('Open Ticket Session', () => {
    test.describe('Ask a chat to open a ticket', () => {
      test.beforeEach(async ({ page }) => {
        await page.getByRole('button', { name: '+ Ticket' }).click()
      })

      test("Then the chat's prompt holds Open a new ticket with ticket.create, titled: for the Person to finish", async () => {
        await expect.poll(() => receivedBy(chat)).toContain('Open a new ticket with ticket.create session=.sessions/checkout-flow/session.json, titled: ')
      })
    })
  })

  test.describe('Close Active Session', () => {
    test.describe('Close the active session from its card', () => {
      test.beforeEach(async ({ page }) => {
        await card(page, 'checkout-flow').getByRole('button', { name: 'Close' }).first().click()
      })

      test('Then the chat is sent /space:session:close-session', async () => {
        await expect.poll(() => receivedBy(chat)).toContain('/space:session:close-session session=.sessions/checkout-flow/session.json')
      })

      test('And checkout-flow stays In progress in Discovery', async ({ page }) => {
        await expect.poll(() => receivedBy(chat)).toContain('/space:session:close-session session=.sessions/checkout-flow/session.json')
        await expect(column(page, 'Discovery').locator('.card-list').first().locator('[data-ticket="checkout-flow"]')).toBeVisible()
      })
    })
  })

  test.describe('Split Ticket Into Child Tickets', () => {
    test.describe('Ask the chat to split a ticket into child tickets', () => {
      test.beforeEach(async ({ page }) => {
        await card(page, 'checkout-flow').getByRole('button', { name: 'Split' }).first().click()
      })

      test("Then the chat's prompt holds Split ticket checkout-flow into child tickets, one per story on its story map: call ticket.create with parent checkout-flow for each story.", async () => {
        await expect.poll(() => receivedBy(chat)).toContain('Split ticket checkout-flow into child tickets, one per story on its story map: call ticket.create with parent checkout-flow for each story. session=.sessions/checkout-flow/session.json')
      })
    })

    test.describe('Keep Split off on a closed ticket', () => {
      test('Then Split is off', async ({ page }) => {
        await expect(card(page, 'shipped-work').getByRole('button', { name: 'Split' }).first()).toBeDisabled()
      })
    })

    test.describe('Keep Split off on a locked ticket', () => {
      test.beforeEach(async ({ page }) => {
        await expect(page.getByRole('switch', { name: 'Active session only' })).toBeChecked()
      })

      test('Then Split is off', async ({ page }) => {
        await expect(card(page, 'billing-report').getByRole('button', { name: 'Split' }).first()).toBeDisabled()
      })
    })
  })

  test.describe('Write Ticket Handoff', () => {
    test.describe('Ask the chat to write a handoff', () => {
      test.beforeEach(async ({ page }) => {
        await card(page, 'checkout-flow').getByRole('button', { name: 'Handoff' }).first().click()
      })

      test("Then the chat's prompt holds Write a handoff for ticket checkout-flow with /space-session-handoff-session.", async () => {
        await expect.poll(() => receivedBy(chat)).toContain('Write a handoff for ticket checkout-flow with /space-session-handoff-session session=.sessions/checkout-flow/session.json')
      })

      // The toast also names the chat: "Queued for the prompt of Steer chat, for you to review: …".
      test('And a toast says Queued for the prompt, for you to review', async ({ page }) => {
        await expect(toast(page, /^Queued for the prompt of Steer chat, for you to review/)).toBeVisible()
      })
    })

    test.describe("Hold the handoff until the chat's turn ends", () => {
      test.beforeEach(async ({ page }) => {
        chat.isBusy = true
        await expect(page.getByRole('option', { name: 'Steer chat (busy)' })).toBeAttached({ timeout: CHAT_CHECKED_IN_MILLISECONDS })
        await card(page, 'checkout-flow').getByRole('button', { name: 'Handoff' }).first().click()
      })

      test('Then a toast says the fill goes in when this turn ends', async ({ page }) => {
        await expect(toast(page, 'It goes in when this turn ends.')).toBeVisible()
      })

      test('And the prompt receives the text once the turn has ended', async ({ page }) => {
        await expect(toast(page, 'It goes in when this turn ends.')).toBeVisible()
        const before = chat.received.length
        chat.isBusy = false
        await expect.poll(() => receivedBy(chat).slice(before)).toContain('Write a handoff for ticket checkout-flow with /space-session-handoff-session session=.sessions/checkout-flow/session.json')
      })
    })
  })
})
