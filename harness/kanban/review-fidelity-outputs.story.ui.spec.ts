/**
 * Review Fidelity Outputs at the browser tier: the scenarios that only the board app's page shows.
 *
 * Scenarios: move-work-forward-on-session-board/review-fidelity-outputs/*\/*_story.test.py. The Python tiers replay
 * the rest from review-fidelity-outputs.story.shared.py.
 *
 * Each scenario runs against the board app built and served on the throwaway fixture project
 * (harness/kanban/app/test-utils/fixture-repo.ts) with its real cdd server. A Given seeds the fixture project's
 * `.sessions/` or its files.
 *
 * Left out here: the toast of List Ticket Files "Say in a toast when the list cannot be read", because the page lists
 * only the tickets the board just read, so a person cannot ask for a ticket the board does not have.
 */
import { rmSync } from 'node:fs'
import { join } from 'node:path'

import { card, expect, fixtureRoot, openBoard, resetSessions, test, writeInto } from './app/tests/story-ui'
import type { Locator, Page } from './app/tests/story-ui'

const STAGE_FILES = ['tests/a.md', 'tests/deep/b.md', 'src/c.ts']

const files = (page: Page) => page.locator('[data-panel="files"]')

async function openStoryMapBar(page: Page, ticket: string, title: string): Promise<Locator> {
  await card(page, ticket).getByRole('button', { name: `Show ${title}` }).click({ position: { x: 4, y: 4 } })
  await page.locator('.details-body [data-tile="stories-story_map"] .tile-name').click()
  const bar = page.locator('.details-body [data-tile="stories-story_map"] .expansion')
  await expect(bar).toBeVisible()
  return bar
}

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

test.describe('Browse Ticket Folder', () => {
  test.describe("Group a stage's files under their folders", () => {
    test.beforeEach(async ({ page }) => {
      for (const path of STAGE_FILES) writeInto(join(fixtureRoot, path), '')
      await openBoard(page)
      await page.locator('.details-bar').getByRole('button', { name: 'Discovery · in progress' }).click()
    })

    test.afterEach(() => {
      for (const path of ['tests/a.md', 'tests/deep', 'src']) rmSync(join(fixtureRoot, path), { recursive: true, force: true })
    })

    // Fails today: no Discovery fidelity declares tests/a.md, tests/deep/b.md, or src/c.ts as its output, so the folder
    // view lists the fidelities' declared files instead; side-panel-client.spec groups these paths as given.
    test('Then the files panel groups a.md and deep/b.md under tests/ and c.ts under src/', async ({ page }) => {
      const groups = files(page).locator('.folder-group')
      await expect(groups.filter({ has: page.locator('.folder-root', { hasText: /^tests\/$/ }) }).locator('.folder-entry')).toHaveText(['a.md', 'deep/b.md'])
      await expect(groups.filter({ has: page.locator('.folder-root', { hasText: /^src\/$/ }) }).locator('.folder-entry')).toHaveText(['c.ts'])
    })
  })
})

test.describe('View Fidelity Files', () => {
  test.describe('Go back to the list when the last tab closes', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
      await (await openStoryMapBar(page, 'checkout-flow', 'Checkout flow')).getByRole('button', { name: 'files', exact: true }).click()
      await expect(files(page).getByRole('tab', { name: 'story-map.md' })).toBeVisible()
      await expect(files(page).getByRole('tab', { name: 'story-map.drawio' })).toBeVisible()
      await files(page).getByRole('button', { name: 'Close story-map.md' }).click()
      await files(page).getByRole('button', { name: 'Close story-map.drawio' }).click()
    })

    test('Then the files panel shows the list', async ({ page }) => {
      await expect(files(page).locator('.file-mode.is-chosen')).toHaveText('folder')
      await expect(files(page).getByRole('tab')).toHaveCount(0)
    })
  })
})

test.describe('Review Fidelity', () => {
  test.describe('Keep Review off until Validate is clean', () => {
    test.beforeEach(async ({ page }) => {
      await openBoard(page)
    })

    test('Then review is off', async ({ page }) => {
      await expect((await openStoryMapBar(page, 'billing-report', 'Billing report')).getByRole('button', { name: 'review', exact: true })).toBeDisabled()
    })
  })
})
