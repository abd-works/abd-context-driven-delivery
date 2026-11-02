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
import { {snake}Behavior } from './{snake}.spec.shared'

itBehavesLike({snake}Behavior, playwrightTier(page => new {Domain}PageDriver(page)))
