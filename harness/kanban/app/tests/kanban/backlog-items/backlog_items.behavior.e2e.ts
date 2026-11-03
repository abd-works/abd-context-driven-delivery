/**
 * Runs the shared behavior through the whole stack: the page, the real server, and the real cdd tools, on the throwaway
 * repository. Nothing here intercepts a request.
 */
import { expect, test } from '@playwright/test'

import { playwrightTier } from 'test-utils/behavior-test/behavior-playwright'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { fixtureRoot, resetSessions } from 'test-utils/fixture-repo'

import { toast } from '../../support'
import { BacklogItemsPageDriver } from './backlog_items.page-driver'
import { backlogItemsBehavior } from './backlog_items.spec.shared'

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

itBehavesLike(backlogItemsBehavior, playwrightTier(page => BacklogItemsPageDriver.fromPage(page)))

// Only the page says these, so they have no shared signature.
test.describe('a backlog item a person acts on', () => {
  test('should say in a toast that it was added', async ({ page }) => {
    await (await BacklogItemsPageDriver.fromPage(page)).add('Gift cards', 'Sell them at the till.')
    await expect(toast(page, 'Gift cards added to Backlog')).toBeVisible()
  })

  test('should say in a toast that it started', async ({ page }) => {
    await (await BacklogItemsPageDriver.fromPage(page)).start('Search the catalog')
    await expect(toast(page, 'Search the catalog started in Discovery')).toBeVisible()
  })
})
