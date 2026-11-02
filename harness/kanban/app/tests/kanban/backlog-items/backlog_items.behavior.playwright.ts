/**
 * Runs the shared behavior through the page, with the API answered from examples, so it proves what shows up.
 * What a person is told gets its own `test` below it, because only the page says it.
 */
import { expect, test } from '@playwright/test'

import { ExampleApi } from 'test-utils/behavior-test/example-api'
import { playwrightTier } from 'test-utils/behavior-test/behavior-playwright'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'

import { toast } from '../../support'
import { backlogItemsBehavior } from './backlog_items.spec.shared'
import { BacklogItemsPageDriver } from './backlog_items.page-driver'
import { BOARD_BEFORE_ITEMS, ITEM_ANSWERS } from './examples/backlog_items.examples'

const opened = async (page: Parameters<typeof BacklogItemsPageDriver.fromPage>[0]) => {
  await new ExampleApi(BOARD_BEFORE_ITEMS, ITEM_ANSWERS).answerOn(page)
  return BacklogItemsPageDriver.fromPage(page)
}

itBehavesLike(backlogItemsBehavior, playwrightTier(opened))

test.describe('a backlog item a person acts on', () => {
  test('should say in a toast that it was added', async ({ page }) => {
    await (await opened(page)).add('Gift cards', 'Sell them at the till.')
    await expect(toast(page, 'Gift cards added to Backlog')).toBeVisible()
  })

  test('should say in a toast that it started', async ({ page }) => {
    await (await opened(page)).start('Search the catalog')
    await expect(toast(page, 'Search the catalog started in Discovery')).toBeVisible()
  })
})
