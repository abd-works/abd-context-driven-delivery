/**
 * Review Fidelity Outputs at the browser tier: the scenarios that only the board app's page shows.
 *
 * Scenarios: story_tests/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md. The Python tiers replay
 * the rest from review-fidelity-outputs.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/` or its files.
 *
 * The board shows no file itself (2026-11-21, proposal 24): each press opens the Files app on what it names, so this
 * tier reads the Files app's link a press opens, with the Files app answered as running. What the Files app then shows,
 * its filters, its list and the open file, is proved by the Files app's own specs
 * (story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/).
 *
 * Left out here: the toast of List Ticket Files "Say in a toast when the list cannot be read", because the page lists
 * only the tickets the board just read, so a person cannot ask for a ticket the board does not have.
 */
import { rmSync } from 'node:fs'
import { join } from 'node:path'

import { card, catchFilesAppLinks, expect, fixtureRoot, openBoard, resetSessions, test, writeInto } from '../../../../space/kanban/app/tests/story-ui'
import type { Locator, Page } from '../../../../space/kanban/app/tests/story-ui'

async function openStoryMapBar(page: Page, ticket: string, title: string): Promise<Locator> {
  await card(page, ticket).getByRole('button', { name: `Show ${title}` }).click({ position: { x: 4, y: 4 } })
  await page.locator('.details-body [data-tile="stories-story-map"] .tile-name').click()
  const bar = page.locator('.details-body [data-tile="stories-story-map"] .expansion')
  await expect(bar).toBeVisible()
  return bar
}

// The board open, with the Files app's links a press opens kept, and what each link names.
async function openedBoard(page: Page): Promise<() => Promise<Record<string, string>[]>> {
  const opened = await catchFilesAppLinks(page)
  await openBoard(page)
  return async () => (await opened()).map(url => Object.fromEntries(url.searchParams))
}

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('View Fidelity Files', () => {
  test.describe("Open the Files app on a fidelity's files", () => {
    test("Then the Files app opens on checkout-flow's story_map files, read through its session", async ({ page }) => {
      const links = await openedBoard(page)
      await (await openStoryMapBar(page, 'checkout-flow', 'Checkout flow')).getByRole('button', { name: 'files', exact: true }).click()
      await expect.poll(async () => (await links()).map(link => [link.files, link.fidelity, link.session])).toEqual([['checkout-flow', 'stories-story-map', '.sessions/checkout-flow/session.json']])
    })
  })
})

test.describe('Open Session Files From Details', () => {
  test.describe('Open the session folder from the session button', () => {
    test('Then the Files app opens on .sessions/checkout-flow', async ({ page }) => {
      const links = await openedBoard(page)
      await page.locator('.details-bar').getByRole('button', { name: 'checkout-flow', exact: true }).click()
      await expect.poll(async () => (await links()).map(link => link['session-folder'])).toEqual(['checkout-flow'])
    })
  })

  test.describe('Open the workpath folder from the details', () => {
    const NOTE = join(fixtureRoot, 'workpath-note.md')

    test.beforeEach(() => writeInto(NOTE, '# A note in the workpath\n'))
    test.afterEach(() => rmSync(NOTE, { force: true }))

    test("Then the Files app opens on the folder checkout-flow's session works in", async ({ page }) => {
      const links = await openedBoard(page)
      await page.locator('.details-bar').getByTitle('Browse the folder the session works in').click()
      await expect.poll(async () => (await links()).map(link => link['workpath-folder'])).toEqual(['checkout-flow'])
    })

    test('But the root chooser does not open', async ({ page }) => {
      const links = await openedBoard(page)
      await page.locator('.details-bar').getByTitle('Browse the folder the session works in').click()
      await expect.poll(async () => (await links()).length).toBe(1)
      await expect(page.getByRole('dialog')).toHaveCount(0)
    })
  })
})
