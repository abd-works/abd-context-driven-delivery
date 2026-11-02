/**
 * Presses and reads what a person presses and reads. The Playwright and e2e tiers share it, so the same steps run
 * against the examples and against the whole stack.
 *
 * ```
 * file: tests/{epicSlug}/{subEpicSlug}/{snake}.page-driver.ts
 * ```
 */
import type { Page } from '@playwright/test'

import type { {Domain}Driver } from './{snake}.spec.shared'

export class {Domain}PageDriver implements {Domain}Driver {
  constructor(private readonly page: Page) {}

  async {operation}({identity}: string): Promise<void> {
    await this.page.getByRole('button', { name: '{control}' }).click()
  }

  async {reading}Of({identity}: string): Promise<string> {
    return this.page.getByTestId(`{reading}-${{identity}}`).innerText()
  }
}
