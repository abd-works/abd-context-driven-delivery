/**
 * Runs the shared behavior through the whole stack: the page, the real server, and the real cdd tools, on the throwaway
 * repository. Nothing here intercepts a request.
 */
import { test } from '@playwright/test'

import { playwrightTier } from 'test-utils/behavior-test/behavior-playwright'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { fixtureRoot, resetSessions } from 'test-utils/fixture-repo'

import { MoveTicketPageDriver } from './move_ticket.page-driver'
import { moveTicketBehavior } from './move_ticket.spec.shared'

test.beforeEach(() => resetSessions(fixtureRoot))
test.afterAll(() => resetSessions(fixtureRoot))

itBehavesLike(moveTicketBehavior, playwrightTier(page => MoveTicketPageDriver.fromPage(page)))
