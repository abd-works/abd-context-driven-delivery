/**
 * Runs the shared behavior through the whole stack: the page, the real server, and the real store or MCP tool, on a
 * throwaway project. It uses the Playwright tier's page driver, and nothing in this file intercepts a request.
 *
 * ```
 * file: tests/{epicSlug}/{subEpicSlug}/{snake}.behavior.e2e.ts
 * ```
 */
import { test } from '@playwright/test'

import { playwrightTier } from 'test-utils/behavior-test/behavior-playwright'
import { itBehavesLike } from 'test-utils/behavior-test/behavior-test'
import { {Domain}PageDriver } from './{snake}.page-driver'
import { {camel}Behavior } from './{snake}.spec.shared'

// A real press really changes the store, so each behavior starts from the same throwaway data.
test.beforeEach(() => {resetThrowawayStore}())

itBehavesLike({camel}Behavior, playwrightTier(page => {Domain}PageDriver.fromPage(page)))
