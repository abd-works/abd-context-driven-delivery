/**
 * Review Fidelity Outputs at the browser tier: the scenarios that only the board app's page shows.
 *
 * Scenarios: harness/.context/stories/move-work-forward-on-session-board/work-fidelity-outputs-on-board/review-fidelity-outputs-on-board/review_fidelity_outputs_on_board_story.test.md. The Python tiers replay
 * the rest from review-fidelity-outputs.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (space/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/` or its files.
 *
 * The fixture's checkout-flow works in Discovery on every practice, so the story map's Files button shows its files with
 * the Stories filter on, and BDD's behavior files a toggle away. Its tickets work on no branch of their own, so none of
 * their files is changed.
 *
 * Left out here: the toast of List Ticket Files "Say in a toast when the list cannot be read", because the page lists
 * only the tickets the board just read, so a person cannot ask for a ticket the board does not have.
 */
import { rmSync } from 'node:fs'
import { join } from 'node:path'

import { card, expect, fixtureRoot, openBoard, resetSessions, test, writeInto } from './app/tests/story-ui'
import type { Locator, Page } from './app/tests/story-ui'

const files = (page: Page) => page.locator('[data-panel="files"]')

async function openStoryMapBar(page: Page, ticket: string, title: string): Promise<Locator> {
  await card(page, ticket).getByRole('button', { name: `Show ${title}` }).click({ position: { x: 4, y: 4 } })
  await page.locator('.details-body [data-tile="stories-story-map"] .tile-name').click()
  const bar = page.locator('.details-body [data-tile="stories-story-map"] .expansion')
  await expect(bar).toBeVisible()
  return bar
}

async function openStoryMapFiles(page: Page): Promise<void> {
  await openBoard(page)
  await (await openStoryMapBar(page, 'checkout-flow', 'Checkout flow')).getByRole('button', { name: 'files', exact: true }).click()
  await expect(files(page).getByRole('tab', { name: 'story-map.md' })).toBeVisible()
}

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('List Ticket Files', () => {
  test.describe("Filter the tabs to the files the ticket's branch changed", () => {
    test.beforeEach(async ({ page }) => {
      await openStoryMapFiles(page)
      await files(page).getByRole('checkbox', { name: 'only changed files' }).check()
    })

    test('Then the tabs show only the changed files, here none', async ({ page }) => {
      await expect(files(page).getByRole('tab')).toHaveCount(0)
    })
  })

  test.describe('Clear the changed-files filter', () => {
    test.beforeEach(async ({ page }) => {
      await openStoryMapFiles(page)
      await files(page).getByRole('checkbox', { name: 'only changed files' }).check()
      await files(page).getByRole('checkbox', { name: 'only changed files' }).uncheck()
    })

    test('Then the tabs show every file again', async ({ page }) => {
      await expect(files(page).getByRole('tab')).toHaveText(['story-map.md', 'story-map.drawio'])
    })
  })
})

test.describe('Browse Ticket Files By Practice', () => {
  test.describe('Show the practice filters and every file as a tab along the top', () => {
    test.beforeEach(async ({ page }) => {
      await openStoryMapFiles(page)
    })

    test('Then the top of the files panel shows a Stories filter and a BDD filter, each by its short form', async ({ page }) => {
      const filters = files(page).getByRole('group', { name: 'File filters' })
      await expect(filters.getByRole('button', { name: 'Stories', exact: true })).toBeVisible()
      await expect(filters.getByRole('button', { name: 'BDD', exact: true })).toBeVisible()
    })

    test("And the tabs below them show the story map's files in Stories' color", async ({ page }) => {
      const tabs = files(page).locator('.file-tab')
      await expect(tabs).toHaveCount(2)
      for (const tab of await tabs.all()) await expect(tab).toHaveAttribute('data-practice', 'stories')
    })
  })

  test.describe("Preset the practice filters from the Files button", () => {
    test.beforeEach(async ({ page }) => {
      await openStoryMapFiles(page)
    })

    test('Then the Stories filter is on', async ({ page }) => {
      await expect(files(page).getByRole('button', { name: 'Stories', exact: true })).toHaveAttribute('aria-pressed', 'true')
    })

    test('But the BDD filter is off, and no BDD tab shows', async ({ page }) => {
      await expect(files(page).getByRole('button', { name: 'BDD', exact: true })).toHaveAttribute('aria-pressed', 'false')
      await expect(files(page).locator('.file-tab[data-practice="bdd"]')).toHaveCount(0)
    })
  })

  test.describe('Turn a practice filter on', () => {
    test.beforeEach(async ({ page }) => {
      await openStoryMapFiles(page)
      await files(page).getByRole('button', { name: 'BDD', exact: true }).click()
      await expect(files(page).locator('.file-tab[data-practice="bdd"]').first()).toBeVisible()
    })

    test("Then BDD's tabs show in BDD's color, after the Stories tabs", async ({ page }) => {
      const practices = await files(page).locator('.file-tab').evaluateAll(tabs => tabs.map(tab => tab.getAttribute('data-practice')))
      expect(practices.slice(0, 2)).toEqual(['stories', 'stories'])
      expect([...new Set(practices.slice(2))]).toEqual(['bdd'])
    })
  })

  test.describe('Select a tab to view its file', () => {
    test.beforeEach(async ({ page }) => {
      await openStoryMapFiles(page)
      await files(page).getByRole('tab', { name: 'story-map.drawio' }).click()
      await files(page).getByRole('tab', { name: 'story-map.md' }).click()
    })

    test('Then the viewer shows .context/story-map.md', async ({ page }) => {
      await expect(files(page).locator('.active-file')).toHaveText('.context/story-map.md')
      await expect(files(page).locator('.markdown-page').getByRole('heading', { name: 'Check Out Order' })).toBeVisible()
    })
  })
})

test.describe('View Fidelity Files', () => {
  test.describe('Open one tab per format, colored by its practice, generated or not', () => {
    test.beforeEach(async ({ page }) => {
      await openStoryMapFiles(page)
    })

    test('Then the tabs along the top show .context/story-map.md and .context/story-map.drawio', async ({ page }) => {
      await expect(files(page).getByRole('tab')).toHaveText(['story-map.md', 'story-map.drawio'])
    })

    test('And the drawio tab says it is not generated yet', async ({ page }) => {
      await files(page).getByRole('tab', { name: 'story-map.drawio' }).click()
      await expect(files(page).getByText('Not generated yet.')).toBeVisible()
    })
  })
})

test.describe('Open Session Files From Details', () => {
  test.describe('Open the session folder from the session button', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await page.locator('.details-bar').getByRole('button', { name: 'checkout-flow', exact: true }).click()
    })

    test('Then the file view shows .sessions/checkout-flow', async ({ page }) => {
      await expect(files(page).locator('.files-subject')).toHaveText('checkout-flow session folder')
      await expect(files(page).getByRole('tab', { name: 'session.log', exact: true })).toBeVisible()
    })
  })

  test.describe('Open the workpath folder from the details', () => {
    const NOTE = join(fixtureRoot, 'workpath-note.md')

    test.beforeEach(async ({ page }) => {
      writeInto(NOTE, '# A note in the workpath\n')
      await openBoard(page)
      await page.locator('.details-bar').getByTitle('Browse the folder the session works in').click()
    })

    test.afterEach(() => rmSync(NOTE, { force: true }))

    test("Then the files panel lists the entries of the session's workpath", async ({ page }) => {
      await expect(files(page).getByRole('tab', { name: 'workpath-note.md', exact: true })).toBeVisible()
    })

    test('But the root chooser does not open', async ({ page }) => {
      await expect(files(page)).toBeVisible()
      await expect(page.getByRole('dialog')).toHaveCount(0)
    })
  })
})
