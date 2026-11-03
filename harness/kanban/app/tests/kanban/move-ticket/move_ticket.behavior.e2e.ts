/**
 * Runs the shared behavior through the whole stack: the page, the real server, and the real cdd tools, on the throwaway
 * repository. Nothing here intercepts a request.
 */
import { expect, test } from '@playwright/test'

import { playwrightTier } from 'test-utils/behavior-test/behavior-playwright'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { fixtureRoot, resetSessions } from 'test-utils/fixture-repo'

import { toast } from '../../support'
import { MoveTicketPageDriver } from './move_ticket.page-driver'
import { moveTicketBehavior } from './move_ticket.spec.shared'

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

itBehavesLike(moveTicketBehavior, playwrightTier(page => MoveTicketPageDriver.fromPage(page)))

// Only the page says these, so they have no shared signature.
test.describe('a ticket a person moves', () => {
  test('should say in a toast that it is done in its stage', async ({ page }) => {
    await (await MoveTicketPageDriver.fromPage(page)).moveNext('move-me')
    await expect(toast(page, 'Move me moved to Discovery · Done')).toBeVisible()
  })

  test('should say in a toast that it moved to the Backlog', async ({ page }) => {
    await (await MoveTicketPageDriver.fromPage(page)).movePrevious('back-to-backlog')
    await expect(toast(page, 'Back to backlog moved to Backlog')).toBeVisible()
  })
})
