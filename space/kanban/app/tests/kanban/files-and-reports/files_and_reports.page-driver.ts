/**
 * Presses and reads what a person presses and reads. The Playwright and e2e tiers share it, so the same steps run
 * against the examples and against the whole stack.
 */
import { expect, type Locator, type Page } from '@playwright/test'

import { card, openBoard } from '../../support'
import type { FilesAndReportsDriver } from './files_and_reports.spec.shared'

export class FilesAndReportsPageDriver implements FilesAndReportsDriver {
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

  private get filesPanel(): Locator {
    return this.page.locator('[data-panel="files"]')
  }

  private get reportPanel(): Locator {
    return this.page.locator('[data-panel="report"]')
  }

  private async openFilesList(ticket: string, fidelity: string): Promise<void> {
    await card(this.page, ticket).locator('.card-hit').click()
    await this.tileOf(fidelity).locator('.tile-name').click()
    await this.tileOf(fidelity).locator('.expansion').getByRole('button', { name: 'files', exact: true }).click()
    await expect(this.filesPanel.getByRole('tab').first()).toBeVisible()
  }

  private async openReport(ticket: string, fidelity: string): Promise<void> {
    await card(this.page, ticket).locator('.card-hit').click()
    await this.tileOf(fidelity).getByRole('button', { name: 'violations' }).click()
    await expect(this.reportPanel).toBeVisible()
  }

  async generatedFilesOf(ticket: string, fidelity: string): Promise<string[]> {
    await this.openFilesList(ticket, fidelity)
    // A tab shows each file by its name; its path from the project is its title, and a file not there yet is marked missing.
    const tabs = await this.filesPanel.locator('[role="tab"]:not(.is-missing)').all()
    return Promise.all(tabs.map(async tab => (await tab.getAttribute('title')) ?? ''))
  }

  async textOfFile(ticket: string, fidelity: string, path: string): Promise<string> {
    await this.openFilesList(ticket, fidelity)
    await this.filesPanel.locator(`[role="tab"][title="${path}"]`).click()
    await expect(this.filesPanel.locator('.file-viewer')).toBeVisible()
    return this.filesPanel.locator('.file-viewer').innerText()
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
