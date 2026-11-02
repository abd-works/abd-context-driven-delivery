/**
 * Runs the shared behavior through the page, with the API answered from examples, so it proves what shows up.
 * Layout and interaction no other tier can see get their own `test` below it.
 *
 * ```
 * file: tests/{epicSlug}/{subEpicSlug}/{snake}.behavior.playwright.ts
 * ```
 */
import { playwrightTier } from 'test-utils/behavior-test/behavior-playwright'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { {Domain}PageDriver } from './{snake}.page-driver'
import { {camel}Behavior } from './{snake}.spec.shared'

itBehavesLike(
  {camel}Behavior,
  playwrightTier(async page => {
    await page.route('**/api/**', route => route.fulfill({ json: {exampleAnswer} }))
    return {Domain}PageDriver.fromPage(page)
  }),
)
