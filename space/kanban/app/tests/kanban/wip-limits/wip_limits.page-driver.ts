/**
 * Presses and reads what a person presses and reads. The Playwright and e2e tiers share it, so the same steps run
 * against the examples and against the whole stack.
 */
import { expect, type Locator, type Page } from '@playwright/test'

import { openBoard } from '../../support'
import type { WipLimitsDriver } from './wip_limits.spec.shared'

export class WipLimitsPageDriver implements WipLimitsDriver {
  private readonly page: Page

  private constructor(page: Page) {
    this.page = page
  }

  static async fromPage(page: Page): Promise<WipLimitsPageDriver> {
    await openBoard(page)
    return new WipLimitsPageDriver(page)
  }

  private column(stage: string): Locator {
    return this.page.locator(`.board-column[data-column="${stage}"]`)
  }

  async setWipLimit(stage: string, limit: number): Promise<void> {
    await this.column(stage).locator('.limit-button').click()
    await this.page.getByRole('spinbutton', { name: `WIP limit for ${stage}` }).fill(String(limit))
    await this.page.getByRole('spinbutton', { name: `WIP limit for ${stage}` }).press('Enter')
    await expect(this.column(stage).locator('.limit-button')).toHaveText(String(limit))
  }

  async limitOf(stage: string): Promise<number> {
    return Number(await this.column(stage).locator('.limit-button').innerText())
  }

  async isOverLimit(stage: string): Promise<boolean> {
    return (await this.column(stage).locator('.stage-head.is-over-limit').count()) > 0
  }
}
