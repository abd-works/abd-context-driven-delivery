/**
 * Runs the shared behavior through the page, with the API answered from examples, so it proves what shows up.
 * What a person is told gets its own `test` below it, because only the page says it.
 */
import { expect, test } from '@playwright/test'

import { ExampleApi } from 'test-utils/behavior-test/example-api'
import { playwrightTier } from 'test-utils/behavior-test/behavior-playwright'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'

import { toast } from '../../support'
import { BOARD_BEFORE_MOVES, MOVES } from './examples/move_ticket.examples'
import { MoveTicketPageDriver } from './move_ticket.page-driver'
import { moveTicketBehavior } from './move_ticket.spec.shared'

const opened = async (page: Parameters<typeof MoveTicketPageDriver.fromPage>[0]) => {
  await new ExampleApi(BOARD_BEFORE_MOVES, MOVES).answerOn(page)
  return MoveTicketPageDriver.fromPage(page)
}

itBehavesLike(moveTicketBehavior, playwrightTier(opened))

test.describe('a ticket a person moves', () => {
  test('should say in a toast that it is done in its stage', async ({ page }) => {
    await (await opened(page)).moveNext('move-me')
    await expect(toast(page, 'Move me moved to Discovery · Done')).toBeVisible()
  })

  test('should say in a toast that it moved to the Backlog', async ({ page }) => {
    await (await opened(page)).movePrevious('back-to-backlog')
    await expect(toast(page, 'Back to backlog moved to Backlog')).toBeVisible()
  })
})
