/**
 * The Playwright tier of a shared behavior: gives `itBehavesLike` Playwright's blocks and a driver built on the page.
 * A driver can take a moment to build, because the page has to open before the first step.
 *
 * ```
 * file: test-utils/behavior-test/behavior-playwright.ts
 * ```
 */
import { expect, test, type Page } from '@playwright/test'

import type { Tier } from './behavior-test'

export function playwrightTier<Driver>(driverOn: (page: Page) => Driver | Promise<Driver>): Tier<Driver> {
  let current: Driver
  test.beforeEach(async ({ page }) => {
    current = await driverOn(page)
  })
  return {
    describe: (name, body) => test.describe(name, body),
    it: (name, body) => test(name, () => body()),
    before: body => test.beforeEach(() => body()),
    expect,
    driver: () => current,
  }
}
