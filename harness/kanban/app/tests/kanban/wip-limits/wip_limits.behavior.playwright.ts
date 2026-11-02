/**
 * Runs the shared behavior through the page, with the API answered from examples, so it proves what shows up.
 */
import { ExampleApi } from 'test-utils/behavior-test/example-api'
import { playwrightTier } from 'test-utils/behavior-test/behavior-playwright'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'

import { BOARD_BEFORE_LIMITS, LIMIT_ANSWERS } from './examples/wip_limits.examples'
import { WipLimitsPageDriver } from './wip_limits.page-driver'
import { wipLimitsBehavior } from './wip_limits.spec.shared'

itBehavesLike(
  wipLimitsBehavior,
  playwrightTier(async page => {
    await new ExampleApi(BOARD_BEFORE_LIMITS, LIMIT_ANSWERS).answerOn(page)
    return WipLimitsPageDriver.fromPage(page)
  }),
)
