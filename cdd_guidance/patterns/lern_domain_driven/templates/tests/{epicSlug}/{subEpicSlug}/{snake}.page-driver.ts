/**
 * Presses and reads what a person presses and reads. The Playwright and e2e tiers share it, so the same steps run
 * against the examples and against the whole stack. Its fields are declared in full, because Playwright strips types
 * from these files and cannot run a parameter property. A step ends once the page shows its result, so a reading
 * after it sees the new state.
 *
 * ```
 * file: tests/{epicSlug}/{subEpicSlug}/{snake}.page-driver.ts
 * ```
 */
import { expect, type Page } from '@playwright/test'

import type { {Domain}Driver } from './{snake}.spec.shared'

export class {Domain}PageDriver implements {Domain}Driver {
  private readonly page: Page

  private constructor(page: Page) {
    this.page = page
  }

  static async fromPage(page: Page): Promise<{Domain}PageDriver> {
    await page.goto('{webPath}')
    return new {Domain}PageDriver(page)
  }

  async {operation}({identity}: string): Promise<void> {
    await this.page.getByRole('button', { name: '{control}' }).click()
    await expect(this.page.getByTestId(`{reading}-${{identity}}`)).toHaveText('{expected}')
  }

  async {reading}Of({identity}: string): Promise<string> {
    return this.page.getByTestId(`{reading}-${{identity}}`).innerText()
  }
}
