/**
 * The Playwright tier of a shared behavior: gives `itBehavesLike` Playwright's blocks and a driver built on the page.
 *
 * ```
 * file: test-utils/behavior-test/behavior-playwright.ts
 * ```
 */
import { expect, test, type Page } from '@playwright/test'

import type { Tier } from './behavior-test'

export function playwrightTier<Driver>(driverOn: (page: Page) => Driver): Tier<Driver> {
  let current: Driver
  test.beforeEach(({ page }) => {
    current = driverOn(page)
  })
  return {
    describe: (name, body) => test.describe(name, body),
    it: (name, body) => test(name, () => body()),
    before: body => test.beforeEach(() => body()),
    expect,
    driver: () => current,
  }
}
