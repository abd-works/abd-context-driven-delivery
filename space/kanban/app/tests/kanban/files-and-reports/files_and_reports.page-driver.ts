/**
 * Presses and reads what a person presses and reads. The Playwright and e2e tiers share it, so the same steps run
 * against the examples and against the whole stack.
 */
import { expect, type Locator, type Page } from '@playwright/test'

import { card, openBoard } from '../../support'
import type { ReportsDriver } from './files_and_reports.spec.shared'

// The board's page reads reports; a ticket's files open in the Files app, which has its own page tier.
export class FilesAndReportsPageDriver implements ReportsDriver {
  private readonly page: Page

  private constructor(page: Page) {
    this.page = page
  }

  static async fromPage(page: Page): Promise<FilesAndReportsPageDriver> {
    await openBoard(page)
    return new FilesAndReportsPageDriver(page)
  }

  private tileOf(fidelity: string): Locator {
    return this.page.locator(`.details-body [data-tile="${fidelity}"]`)
  }

  private get reportPanel(): Locator {
    return this.page.locator('[data-panel="report"]')
  }

  private async openReport(ticket: string, fidelity: string): Promise<void> {
    await card(this.page, ticket).locator('.card-hit').click()
    await this.tileOf(fidelity).getByRole('button', { name: 'violations' }).click()
    await expect(this.reportPanel).toBeVisible()
  }

  async reportPathOf(ticket: string, fidelity: string): Promise<string> {
    await this.openReport(ticket, fidelity)
    return this.reportPanel.locator('.panel-subtitle').first().innerText()
  }

  async ruleNamesOf(ticket: string, fidelity: string): Promise<string[]> {
    await this.openReport(ticket, fidelity)
    return this.reportPanel.locator('.rule-toggle > span:not(.rule-count)').allInnerTexts()
  }

  async failingLineOf(ticket: string, fidelity: string): Promise<number> {
    await this.openReport(ticket, fidelity)
    return Number(await this.reportPanel.locator('.code-line.is-failing .line-number').innerText())
  }
}
