/**
 * See Work On Session Board at the browser tier: the scenarios whose behaviour lives only in the board app.
 *
 * Scenarios: move-work-forward-on-session-board/see-work-on-session-board/*\/*_story.test.py. The Python tiers replay
 * the rest from see-work-on-session-board.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (harness/kanban/app/test-utils/fixture-repo.ts) with its real cdd server, as the board app's own Playwright specs do.
 * A Given seeds the fixture project's `.sessions/`, where the board reads it; a When does what the person does on the
 * page; a Then reads what the person sees.
 *
 * Left out here: "Update the board and cdd to the latest code" and "Say which update step failed" (an update really pulls,
 * builds, and re-pins this checkout; board-client.spec drives it with the steps recorded), "Keep the newer board when an older read answers late" (a browser cannot hold one answer back;
 * board-client.spec drives the page's reads in order), and "Find the board from a chat" and "Name the active ticket on
 * the chat's status line" (the cdd-board mod in harness/chat-ui, not the board app, does them).
 */
import { existsSync } from 'node:fs'
import { join } from 'node:path'

import { ACCENT, BOARD_POST_HEADERS, card, dragCard, expect, FakeChat, fixtureRoot, generatedLine, openBoard, openCard, openCardOf, resetSessions, seedActive, startBoard, test, toast, turnOffActiveSessionOnly, validatedLine, waitForChat, writeInto, writeSession } from './app/tests/story-ui'
import type { Page } from './app/tests/story-ui'

const PAGE_HEIGHT = 900
// billing-report's latest session log line, a day after the fixture's own.
const LATEST_STAMP = '2026-11-02T10:00:00Z'
const BROKEN_BOARD_PORT = 8782
const ACTIVE_BORDER = '3px'
const DISCOVERY_FIDELITIES = ['stories-story_map', 'ddd-bounded_context', 'ux-ia', 'clean_engineering-modules', 'bdd-behavior']

const region = (page: Page, name: 'board' | 'details') => page.locator(`.${name}-region`)
const heightOf = async (page: Page, name: 'board' | 'details') => (await region(page, name).boundingBox())!.height

async function resizeBoardTo(page: Page, wanted: number): Promise<void> {
  const grip = (await page.locator('.grip').boundingBox())!
  const distance = wanted - (await heightOf(page, 'board'))
  await page.mouse.move(grip.x + 200, grip.y + grip.height / 2)
  await page.mouse.down()
  await page.mouse.move(grip.x + 200, grip.y + grip.height / 2 + distance, { steps: 4 })
  await page.mouse.up()
}

async function resizePanelTo(page: Page, kind: string, wanted: number): Promise<void> {
  const panel = (await page.locator(`[data-panel="${kind}"]`).boundingBox())!
  await page.mouse.move(panel.x + 1, 400)
  await page.mouse.down()
  await page.mouse.move(panel.x + 1 - (wanted - panel.width), 400, { steps: 4 })
  await page.mouse.up()
}

const openFilesOf = (page: Page, ticket: string) => card(page, ticket).getByRole('button', { name: 'folder' }).first().click()
const openReportOf = (page: Page, ticket: string) => card(page, ticket).locator('.card-violations').click()

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('Open Board', () => {
  test.describe('Open the board on a project', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
    })

    test('Then the header reads cdd-board-surface-fixture · 9 tickets · active: Checkout flow', async ({ page }) => {
      await expect(page.locator('.header-meta')).toHaveText('cdd-board-surface-fixture · 9 tickets · active: Checkout flow')
    })

    test('And the session board reads the board again every two seconds', async ({ page }) => {
      writeSession(fixtureRoot, { name: 'pet-visits', title: 'Pet visits' })
      await expect(card(page, 'pet-visits')).toBeVisible({ timeout: 4_000 })
    })
  })
})

test.describe('Display Board', () => {
  test.describe('Say the cdd server is not connected', () => {
    // A board of its own whose cdd cannot start, because the program it names does not exist.
    let stop: () => void = () => undefined

    test.beforeEach(async ({ page }) => {
      const board = await startBoard(BROKEN_BOARD_PORT, { CDD_PYTHON: join(fixtureRoot, 'no-such-python.exe') })
      stop = board.stop
      await page.goto(board.url)
    })

    test.afterEach(() => stop())

    // Fails today, most runs: a board whose CDD_PYTHON names no program often shows no band, as
    // story-actions.spec's own 'should show a band when cdd cannot be reached' also finds. The scenario words it "The
    // cdd server is not connected"; the band's text is "cdd is not connected".
    test('Then a band across the top of the page says The cdd server is not connected', async ({ page }) => {
      await expect(page.locator('.band-failure')).toContainText('cdd is not connected', { timeout: 15_000 })
    })

    test('And the header offers Update', async ({ page }) => {
      await expect(page.getByRole('button', { name: 'Update' })).toBeVisible({ timeout: 15_000 })
    })
  })

  test.describe('Show a failing tool in a toast', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      writeInto(join(fixtureRoot, '.sessions', 'broken', 'session.json'), '{broken')
    })

    test('Then a toast says cdd board.show failed: JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)', async ({ page }) => {
      await expect(toast(page, 'cdd board.show failed: JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)').first()).toBeVisible({ timeout: 8_000 })
    })

    test('But no band says the cdd server is lost', async ({ page }) => {
      await expect(toast(page, /board\.show failed/).first()).toBeVisible({ timeout: 8_000 })
      await expect(page.locator('.band-failure')).toHaveCount(0)
    })
  })

  test.describe('Announce a ticket that moved', () => {
    test.beforeEach(async ({ page, request }) => {
      await openBoard(page)
      await expect(card(page, 'move-me')).toBeVisible()
      await request.post('/api/ticket/move-me/move-next', { headers: BOARD_POST_HEADERS })
    })

    test('Then a toast says Move me moved to Discovery · Done', async ({ page }) => {
      await expect(toast(page, 'Move me moved to Discovery · Done')).toBeVisible({ timeout: 8_000 })
    })
  })

  test.describe('Announce a reviewed fidelity', () => {
    test.beforeEach(async ({ page, request }) => {
      writeSession(fixtureRoot, { name: 'billing-report', title: 'Billing report', log: [generatedLine('stories', 'story_map'), validatedLine('Stories', 'story_map')] })
      await openBoard(page)
      await expect(card(page, 'billing-report')).toBeVisible()
      await request.post('/api/fidelity-progress/billing-report/stories-story_map/finish-review', { headers: BOARD_POST_HEADERS, data: {} })
    })

    test('Then a toast says stories-story_map reviewed on billing-report', async ({ page }) => {
      await expect(toast(page, 'stories-story_map reviewed on billing-report')).toBeVisible({ timeout: 8_000 })
    })
  })
})

test.describe('Arrange Board And Details', () => {
  test.describe('Give the board more height', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await resizeBoardTo(page, 300)
    })

    test('Then the board region is 300 pixels high and the details take the rest', async ({ page }) => {
      const details = (await region(page, 'details').boundingBox())!
      const main = (await page.locator('.board-main').boundingBox())!
      expect([await heightOf(page, 'board'), Math.round(details.y + details.height)]).toEqual([300, Math.round(main.y + main.height)])
    })
  })

  test.describe('Keep both regions open', () => {
    // The page is the main region the board and the details share, so the band over it is added to the window.
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      const main = await page.locator('.board-main').evaluate(element => element.clientHeight)
      await page.setViewportSize({ width: 1600, height: PAGE_HEIGHT + (PAGE_HEIGHT - main) })
      await resizeBoardTo(page, 10)
    })

    test('Then the board region stays 160 pixels high', async ({ page }) => {
      expect(await heightOf(page, 'board')).toBe(160)
    })

    test.describe('the Person resizes the board to 5000 pixels', () => {
      test.beforeEach(async ({ page }) => {
        await resizeBoardTo(page, 5000)
      })

      // The largest board leaves the details 160 pixels and the header 90 of the page's main region.
      test('Then the board region stops at 650 pixels, so the details stay open', async ({ page }) => {
        expect(await heightOf(page, 'board')).toBe(650)
      })
    })
  })

  test.describe('Expand one region and show both again', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await page.getByRole('button', { name: 'Expand board' }).click()
    })

    test('Then the board takes the whole page', async ({ page }) => {
      await expect(region(page, 'details')).toHaveCount(0)
    })

    test.describe('the Person collapses the board', () => {
      test.beforeEach(async ({ page }) => {
        await page.getByRole('button', { name: 'Collapse board' }).click()
      })

      test('Then the board and the details share the page again', async ({ page }) => {
        await expect(region(page, 'board').and(page.locator(':visible'))).toHaveCount(1)
        await expect(region(page, 'details')).toBeVisible()
      })
    })
  })
})

test.describe('Display Ticket Card', () => {
  test.describe("Draw the card's title, age, and fidelity segments", () => {
    test.beforeEach(async ({ page }) => {
      // checkout-flow was last worked on at 2026-11-01T10:00:00Z, the fixture's stamp; the page is opened 13 hours later.
      await page.clock.setFixedTime(new Date('2026-11-01T23:00:00Z'))
      await openBoard(page)
    })

    test('Then the card reads Checkout flow and 13 hours ago', async ({ page }) => {
      await expect(card(page, 'checkout-flow').locator('.ticket-title-line .ticket-title').first()).toHaveText('Checkout flow')
      await expect(card(page, 'checkout-flow').locator('.ticket-meta').first()).toHaveText('13 hours ago')
    })

    test('And it shows one segment for each enabled Discovery fidelity, the story_map segment in the violations colour and the rest dim', async ({ page }) => {
      const segments = card(page, 'checkout-flow').locator('.segments').first().locator('.segment')
      await expect(segments).toHaveCount(DISCOVERY_FIDELITIES.length)
      const opacities = await segments.evaluateAll(shown => shown.map(segment => Number(getComputedStyle(segment).opacity)))
      expect([opacities[0]! > opacities[1]!, opacities.slice(1).every(opacity => opacity === opacities[1])]).toEqual([true, true])
    })

    test('And a violations link on the card opens the report', async ({ page }) => {
      await openReportOf(page, 'checkout-flow')
      await expect(page.locator('[data-panel="report"]')).toBeVisible()
    })
  })

  test.describe('Outline the active ticket', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
    })

    test('Then the checkout-flow card has a thick orange outline', async ({ page }) => {
      await expect(card(page, 'checkout-flow')).toHaveCSS('border-top-width', ACTIVE_BORDER)
      await expect(card(page, 'checkout-flow')).toHaveCSS('border-top-color', ACCENT)
    })
  })
})

test.describe('Display Ticket Details', () => {
  test.describe('Show the active ticket with no card pressed', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
    })

    test('Then the details show Checkout flow', async ({ page }) => {
      await expect(page.locator('.details-title h2')).toHaveText('Checkout flow')
    })
  })

  test.describe('Show the ticket worked on last when none is active', () => {
    test.beforeEach(async ({ page }) => {
      seedActive('')
      writeSession(fixtureRoot, { name: 'billing-report', title: 'Billing report', log: [generatedLine('stories', 'story_map', LATEST_STAMP)] })
      await openBoard(page)
    })

    test('Then the details show Billing report', async ({ page }) => {
      await expect(page.locator('.details-title h2')).toHaveText('Billing report')
    })
  })

  test.describe('Say another session must be activated to act on a locked ticket', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await expect(page.getByRole('switch', { name: 'Active session only' })).toBeChecked()
      await card(page, 'billing-report').getByRole('button', { name: 'Show Billing report' }).click({ position: { x: 4, y: 4 } })
    })

    test('Then the details say Activate this session to run actions', async ({ page }) => {
      await expect(page.locator('.details-bar')).toContainText('Activate this session to run actions')
    })
  })

  test.describe("Expand one ticket's card at a time", () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await openCardOf(page, 'checkout-flow')
      await openCardOf(page, 'billing-report')
    })

    test("Then billing-report's card is expanded with a tile for each enabled Discovery fidelity", async ({ page }) => {
      await expect(openCard(page, 'billing-report').locator('[data-tile]')).toHaveCount(DISCOVERY_FIDELITIES.length)
    })

    test("And checkout-flow's card is closed", async ({ page }) => {
      await expect(openCard(page, 'checkout-flow')).toHaveCount(0)
    })
  })

  test.describe('Open a card on the fidelity of a pressed segment', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await card(page, 'billing-report').getByRole('button', { name: /practices-stories-stories-story-map/ }).first().click()
    })

    test("Then billing-report's card is expanded with the story_map tile's action bar open", async ({ page }) => {
      await expect(openCard(page, 'billing-report').locator('[data-tile="stories-story_map"] .expansion')).toBeVisible()
    })
  })
})

test.describe('Set Stage WIP Limit', () => {
  test.describe('Change nothing for a limit that is not a whole number', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await page.getByRole('button', { name: 'WIP limit for Discovery is 3. Edit' }).click()
      await page.getByRole('spinbutton', { name: 'WIP limit for Discovery' }).focus()
      await page.keyboard.press('Control+A')
      await page.keyboard.type('many')
      await page.keyboard.press('Enter')
    })

    test('Then Discovery still shows the limit 3', async ({ page }) => {
      await expect(page.getByRole('button', { name: 'WIP limit for Discovery is 3. Edit' })).toBeVisible()
    })

    test('But no limit is saved', () => {
      expect(existsSync(join(fixtureRoot, '.sessions', '_board.json'))).toBe(false)
    })
  })
})

test.describe('Arrange Side Panel', () => {
  test.describe("Set a panel's width", () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await openFilesOf(page, 'checkout-flow')
      await expect(page.locator('[data-panel="files"]')).toBeVisible()
      await resizePanelTo(page, 'files', 700)
    })

    test('Then the files panel is 700 pixels wide', async ({ page }) => {
      expect((await page.locator('[data-panel="files"]').boundingBox())!.width).toBe(700)
    })

    test.describe('the Person narrows the files panel to 10 pixels', () => {
      test.beforeEach(async ({ page }) => {
        await resizePanelTo(page, 'files', 10)
      })

      test('Then the files panel stops at 360 pixels', async ({ page }) => {
        expect((await page.locator('[data-panel="files"]').boundingBox())!.width).toBe(360)
      })
    })
  })

  test.describe('Expand one panel at a time', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await openReportOf(page, 'checkout-flow')
      await openFilesOf(page, 'checkout-flow')
      await page.getByRole('button', { name: 'Expand report' }).click()
      await page.getByRole('button', { name: 'Expand files' }).click()
    })

    test("Then the files panel takes the board's width less the other open panels", async ({ page }) => {
      const files = (await page.locator('[data-panel="files"]').boundingBox())!.width
      const report = (await page.locator('[data-panel="report"]').boundingBox())!.width
      expect(Math.round(files + report)).toBe(1600)
    })

    test('And the report panel is no longer expanded', async ({ page }) => {
      await expect(page.getByRole('button', { name: 'Expand report' })).toBeVisible()
    })
  })

  test.describe('Close a side panel', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await openReportOf(page, 'checkout-flow')
      await expect(page.locator('[data-panel="report"]')).toBeVisible()
      await page.getByRole('button', { name: 'Close report' }).click()
    })

    test('Then no side panel is open', async ({ page }) => {
      await expect(page.locator('[data-panel]')).toHaveCount(0)
    })
  })

  test.describe("Keep the columns' width when a panel opens", () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await openFilesOf(page, 'checkout-flow')
      await expect(page.locator('[data-panel="files"]')).toBeVisible()
    })

    // The canvas's five columns are 1488 pixels wide together.
    test('Then the columns keep their width and scroll sideways beside the files panel', async ({ page }) => {
      const scrolls = await page.locator('.board-region').evaluate(element => element.scrollWidth > element.clientWidth)
      expect([scrolls, (await page.locator('.column-grid').first().boundingBox())!.width >= 1488]).toEqual([true, true])
    })
  })
})

test.describe('Restrict Actions To Active Session', () => {
  let chat: FakeChat

  test.beforeAll(async ({ playwright, baseURL }) => {
    chat = new FakeChat(await playwright.request.newContext({ baseURL }), 'see-work-chat', 'See work chat')
    await chat.start()
  })

  test.afterAll(() => chat.stop())

  test.describe('Lock tickets that are not the active session', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await waitForChat(page, chat)
      await expect(page.getByRole('switch', { name: 'Active session only' })).toBeChecked()
      await card(page, 'billing-report').getByRole('button', { name: 'Show Billing report' }).click({ position: { x: 4, y: 4 } })
    })

    test("Then billing-report's Run next, Run, practice switches, Split, and Handoff are off", async ({ page }) => {
      const billing = card(page, 'billing-report')
      const opened = await openCardOf(page, 'billing-report')
      await opened.locator('.tile-name').first().click()
      const controls = [billing.getByRole('button', { name: /^Run next/ }).first(), opened.getByRole('button', { name: 'Run', exact: true }).first(), page.getByRole('switch', { name: 'Disable UX for Billing report' }), billing.getByRole('button', { name: 'Split' }).first(), billing.getByRole('button', { name: 'Handoff' }).first()]
      for (const control of controls) await expect(control).toBeDisabled()
    })

    test("And billing-report's Run next says Activate this session to run its next step", async ({ page }) => {
      await expect(card(page, 'billing-report').getByRole('button', { name: /^Run next/ }).first()).toHaveAttribute('title', 'Activate this session to run its next step')
    })

    test("And checkout-flow's actions stay on", async ({ page }) => {
      await expect(card(page, 'checkout-flow').getByRole('button', { name: 'Handoff' }).first()).toBeEnabled()
    })
  })

  test.describe('Keep information and moves open on a locked ticket', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await openFilesOf(page, 'billing-report')
    })

    test("Then the files panel lists billing-report's files", async ({ page }) => {
      await expect(page.locator('[data-panel="files"] .files-subject')).toContainText('stories-story-map')
    })

    test.describe('the Person moves billing-report to Specification', () => {
      test.beforeEach(async ({ page }) => {
        const specification = page.locator('.board-column[data-column="Specification"] .card-list').first()
        await specification.scrollIntoViewIfNeeded()
        await dragCard(page, card(page, 'billing-report'), specification)
      })

      test('Then billing-report moves to Specification', async ({ page }) => {
        await expect(page.locator('.board-column[data-column="Specification"] [data-ticket="billing-report"]')).toBeVisible({ timeout: 8_000 })
      })

      test('And Activate stays on for billing-report', async ({ page }) => {
        await expect(card(page, 'billing-report').getByRole('button', { name: 'Activate' }).first()).toBeEnabled()
      })
    })
  })

  test.describe('Unlock every ticket', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await waitForChat(page, chat)
      await turnOffActiveSessionOnly(page)
    })

    test("Then billing-report's actions are on like the active ticket's", async ({ page }) => {
      await expect(card(page, 'billing-report').getByRole('button', { name: 'Handoff' }).first()).toBeEnabled()
      await expect(card(page, 'billing-report').getByRole('button', { name: /^Run next/ }).first()).toBeEnabled()
    })
  })
})

