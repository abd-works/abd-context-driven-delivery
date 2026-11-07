/**
 * Guide Work Through Practices at the browser tier: the scenarios, and the Thens of the Python tiers' scenarios, that
 * only the board app's page shows.
 *
 * Scenarios: move-work-forward-on-session-board/guide-work-through-practices/*\/*_story.test.py. The Python tiers
 * replay the rest from guide-work-through-practices.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/`; a chat is `FakeChat`, which checks in through the board's server as the cdd-board mod does.
 *
 * Left out here: Add Active Ticket To System Prompt (all three), because the cdd-board mod in harness/chat-ui composes
 * the system prompt, not the board app.
 */

import { card, expect, FakeChat, fixtureRoot, generatedLine, openBoard, openCardOf, receivedBy, resetSessions, seedActive, test, toast, turnOffActiveSessionOnly, waitForChat, waitForNoChat, writeSession } from './app/tests/story-ui'
import type { Locator, Page } from './app/tests/story-ui'

const RESTING_MILLISECONDS = 500
const STILL_CLOSED_MILLISECONDS = 800

const details = (page: Page) => page.locator('.details-body')
const tileIn = (where: Locator, slug: string) => where.locator(`[data-tile="${slug}"]`)
const barOf = (where: Locator, slug: string) => tileIn(where, slug).locator('.expansion')
const pressTile = (where: Locator, slug: string) => tileIn(where, slug).locator('.tile-name').click()

async function selectTicket(page: Page, ticket: string, title: string): Promise<void> {
  await card(page, ticket).getByRole('button', { name: `Show ${title}` }).click({ position: { x: 4, y: 4 } })
  await expect(page.locator('.details-title h2')).toHaveText(title)
}

// A card low in a stage drags onto the part of the Done list the board region shows, since the list's own middle can
// be scrolled out of sight.
async function dragIntoView(page: Page, dragged: Locator, target: Locator): Promise<void> {
  const [from, to, shown] = [(await dragged.boundingBox())!, (await target.boundingBox())!, (await page.locator('.board-region').boundingBox())!]
  await page.mouse.move(from.x + 24, from.y + 14)
  await page.mouse.down()
  await page.mouse.move(from.x + 44, from.y + 24, { steps: 10 })
  await page.mouse.move(to.x + to.width / 2, Math.max(to.y, shown.y) + 40, { steps: 10 })
  await page.mouse.up()
}

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('with no chat connected', () => {
  test.describe('Open Practice Tile', () => {
    test.describe('Open a tile on a short hover', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        const opened = await openCardOf(page, 'billing-report')
        await tileIn(opened, 'stories-story-map').hover()
        await page.waitForTimeout(RESTING_MILLISECONDS)
      })

      test("Then the story_map tile's action bar opens above the grid, at full width", async ({ page }) => {
        const opened = page.locator('[data-open-card="billing-report"]')
        await expect(opened.locator('.expansion')).toBeVisible()
        const inside = await opened.evaluate(element => element.clientWidth - parseFloat(getComputedStyle(element).paddingLeft) - parseFloat(getComputedStyle(element).paddingRight))
        expect((await opened.locator('.expansion').boundingBox())!.width).toBeGreaterThanOrEqual(inside - 1)
      })

      test.describe('the Person moves the pointer away', () => {
        test.beforeEach(async ({ page }) => {
          await expect(page.locator('[data-open-card="billing-report"] .expansion')).toBeVisible()
          await page.locator('.board-header').hover()
        })

        test('Then the action bar closes', async ({ page }) => {
          await expect(page.locator('[data-open-card="billing-report"] .expansion')).toHaveCount(0)
        })
      })
    })

    test.describe('Keep a pressed tile open', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await selectTicket(page, 'billing-report', 'Billing report')
        await pressTile(details(page), 'stories-story-map')
        await page.locator('.board-header').hover()
        await page.waitForTimeout(STILL_CLOSED_MILLISECONDS)
      })

      test('Then the story_map action bar stays open after the pointer leaves', async ({ page }) => {
        await expect(barOf(details(page), 'stories-story-map')).toBeVisible()
      })

      test.describe('the Person presses the story_map tile again', () => {
        test.beforeEach(async ({ page }) => {
          await pressTile(details(page), 'stories-story-map')
        })

        test('Then the story_map action bar closes', async ({ page }) => {
          await expect(barOf(details(page), 'stories-story-map')).toHaveCount(0)
        })
      })
    })

    test.describe('Keep two pressed tiles open at once', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        // A bar's action is off on a ticket that is not the active session while Active session only is on.
        await turnOffActiveSessionOnly(page)
        await selectTicket(page, 'billing-report', 'Billing report')
        await pressTile(details(page), 'stories-story-map')
        await pressTile(details(page), 'ddd-bounded-context')
      })

      test('Then both action bars are open', async ({ page }) => {
        await expect(details(page).locator('[data-tile="stories-story-map"] .expansion, [data-tile="ddd-bounded-context"] .expansion')).toHaveCount(2)
      })

      test.describe('the Person chooses sketch on the bounded_context bar', () => {
        test.beforeEach(async ({ page }) => {
          await barOf(details(page), 'ddd-bounded-context').getByRole('combobox', { name: 'Action' }).selectOption('sketch')
        })

        test("Then only the bounded_context bar's action is sketch", async ({ page }) => {
          const actions = [await barOf(details(page), 'ddd-bounded-context').getByRole('combobox', { name: 'Action' }).inputValue(), await barOf(details(page), 'stories-story-map').getByRole('combobox', { name: 'Action' }).inputValue()]
          expect(actions).toEqual(['sketch', 'generate'])
        })
      })
    })

    test.describe('Open a hovered tile beside a pressed one', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        const opened = await openCardOf(page, 'billing-report')
        await pressTile(opened, 'stories-story-map')
        await tileIn(opened, 'ux-ia').hover()
        await page.waitForTimeout(RESTING_MILLISECONDS)
      })

      test('Then the ia bar opens beside the story_map bar', async ({ page }) => {
        await expect(page.locator('[data-open-card="billing-report"] .expansion')).toHaveCount(2)
      })

      test.describe('the Person moves the pointer away from the ia tile', () => {
        test.beforeEach(async ({ page }) => {
          await expect(page.locator('[data-open-card="billing-report"] .expansion')).toHaveCount(2)
          await page.locator('.board-header').hover()
        })

        test('Then the ia bar closes and the story_map bar stays open', async ({ page }) => {
          await expect(page.locator('[data-open-card="billing-report"] .expansion')).toHaveCount(1)
          await expect(barOf(page.locator('[data-open-card="billing-report"]'), 'stories-story-map')).toBeVisible()
        })
      })
    })

    test.describe('Leave a tile in the details closed under a resting pointer', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await selectTicket(page, 'billing-report', 'Billing report')
        await tileIn(details(page), 'stories-story-map').hover()
        await page.waitForTimeout(STILL_CLOSED_MILLISECONDS)
      })

      test('Then the story_map action bar stays closed', async ({ page }) => {
        await expect(barOf(details(page), 'stories-story-map')).toHaveCount(0)
      })
    })
  })

  test.describe('Send Action To Stage Practices', () => {
    test.describe('Keep two stage heads open at once', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await selectTicket(page, 'billing-report', 'Billing report')
        await details(page).getByRole('button', { name: 'Actions for Discovery' }).click()
        await details(page).getByRole('button', { name: 'Actions for Specification' }).click()
      })

      test('Then both stage bars are open', async ({ page }) => {
        await expect(details(page).getByRole('button', { name: /^Actions for (Discovery|Specification)$/ }).and(page.locator('[aria-expanded="true"]'))).toHaveCount(2)
      })
    })
  })

  test.describe('Choose Ticket Practices', () => {
    test.describe('Turn a practice off for a ticket', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await pressTile(details(page), 'ddd-bounded-context')
        await expect(barOf(details(page), 'ddd-bounded-context')).toBeVisible()
        await page.getByRole('switch', { name: 'Disable DDD for Checkout flow' }).click()
      })

      test('Then a toast says DDD off for Checkout flow · saved to .sessions/checkout-flow/session.json', async ({ page }) => {
        await expect(toast(page, 'DDD off for Checkout flow · saved to .sessions/checkout-flow/session.json')).toBeVisible()
      })

      test('And the bounded_context tile closes and fades', async ({ page }) => {
        await expect(barOf(details(page), 'ddd-bounded-context')).toHaveCount(0)
        await expect(tileIn(details(page), 'ddd-bounded-context')).toHaveCSS('opacity', '0.12')
      })
    })

    test.describe('Keep practice switches off on a locked ticket', () => {
      test.beforeEach(async ({ page }) => {
        await openBoard(page)
        await expect(page.getByRole('switch', { name: 'Active session only' })).toBeChecked()
        await selectTicket(page, 'billing-report', 'Billing report')
      })

      test('Then each practice switch is off until Active session only is turned off', async ({ page }) => {
        // The details name each practice the board sends, so every switch the details show is checked.
        const switches = details(page).getByRole('switch', { name: /^Disable .+ for Billing report$/ })
        await expect(switches.first()).toBeVisible()
        for (const practiceSwitch of await switches.all()) await expect(practiceSwitch).toBeDisabled()
      })
    })
  })

  test.describe('Mark Ticket Done In Stage', () => {
    test.describe('Mark a ticket done in its stage', () => {
      test.beforeEach(async ({ page }) => {
        writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits', log: [generatedLine('stories', 'story_map')] })
        await openBoard(page)
        await card(page, 'pet-visits').scrollIntoViewIfNeeded()
        await dragIntoView(page, card(page, 'pet-visits'), page.locator('.board-column[data-column="Discovery"] .card-list').nth(1))
      })

      test('Then a toast says Pet visits moved to Discovery · Done', async ({ page }) => {
        await expect(toast(page, 'Pet visits moved to Discovery · Done')).toBeVisible({ timeout: 8_000 })
      })
    })
  })

  test.describe('Send Next Fidelity Action', () => {
    test.describe('Keep Run next off where it cannot run', () => {
      test.beforeEach(async ({ page }) => {
        seedActive('billing-report')
        await openBoard(page)
        await waitForNoChat(page)
      })

      test('Then Run next is off', async ({ page }) => {
        await expect(card(page, 'billing-report').getByRole('button', { name: 'Run next: generate' }).first()).toBeDisabled()
      })
    })
  })
})

test.describe('with a chat connected', () => {
  let chat: FakeChat

  test.beforeAll(async ({ playwright, baseURL }) => {
    chat = new FakeChat(await playwright.request.newContext({ baseURL }), 'guide-chat', 'Guide chat')
    await chat.start()
  })

  test.afterAll(() => chat.stop())

  test.describe('Send Action To Stage Practices', () => {
    test.describe('Sketch every fidelity of a stage in one command', () => {
      test.beforeEach(async ({ page }) => {
        seedActive('billing-report')
        await openBoard(page)
        await waitForChat(page, chat)
        await details(page).getByRole('button', { name: 'Actions for Discovery' }).click()
        const bar = details(page).locator('.expansion').first()
        await bar.getByRole('combobox', { name: 'Action' }).selectOption('sketch')
        if ((await bar.getByRole('button', { name: /selected$/ }).count()) === 0) await bar.locator('.format-icon').first().click()
        await bar.getByRole('button', { name: 'Run', exact: true }).click()
      })

      // The command also names the ticket's session.json, because a command runs in whichever chat it is sent to.
      test('Then the chat receives the command /actions-sketch stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior', async () => {
        await expect.poll(() => receivedBy(chat)).toContain('/actions-sketch stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior session=.sessions/billing-report/session.json')
      })
    })
  })

  test.describe('Send Next Fidelity Action', () => {
    test.describe('Fill the prompt to validate', () => {
      test.beforeEach(async ({ page }) => {
        seedActive('back-to-backlog')
        await openBoard(page)
        await waitForChat(page, chat)
        await card(page, 'back-to-backlog').getByRole('button', { name: 'Run next: validate' }).first().click()
      })

      // The command also names the ticket's session.json, because a command runs in whichever chat it is sent to.
      test("Then the chat's prompt holds /actions-validate stories-story-map", async () => {
        await expect.poll(() => chat.received.filter(command => command.kind === 'fill').map(command => command.text)).toContain('/actions-validate stories-story-map session=.sessions/back-to-backlog/session.json')
      })
    })
  })
})
