/**
 * Presses and reads what a person presses and reads. The Playwright and e2e tiers share it, so the same steps run
 * against the examples and against the whole stack.
 */
import { expect, type Locator, type Page } from '@playwright/test'

import { card, openBoard, turnOffActiveSessionOnly } from '../../support'
import type { BacklogItemsDriver } from './backlog_items.spec.shared'

// A segment names its skill and the state of that fidelity's work, as `/practices-stories-stories-story-map: in progress`.
const STATE_WORDS: Record<string, string> = { 'in progress': 'in_progress', 'not started': 'not_started', reviewed: 'done', violations: 'violations' }

export class BacklogItemsPageDriver implements BacklogItemsDriver {
  private readonly page: Page

  private constructor(page: Page) {
    this.page = page
  }

  static async fromPage(page: Page): Promise<BacklogItemsPageDriver> {
    await openBoard(page)
    await turnOffActiveSessionOnly(page)
    return new BacklogItemsPageDriver(page)
  }

  private item(title: string): Locator {
    return this.page.locator(`.ticket-card[data-item="${title}"]`)
  }

  private ticketTitled(title: string): Locator {
    return this.page.locator('.ticket-card[data-ticket]').filter({ has: this.page.getByText(title, { exact: true }) })
  }

  async add(title: string, text: string): Promise<void> {
    await this.page.getByRole('button', { name: 'New backlog ticket' }).click()
    await this.page.getByRole('textbox', { name: 'Title' }).fill(title)
    await this.page.getByRole('textbox', { name: 'Text' }).fill(text)
    await this.page.getByRole('button', { name: 'Add', exact: true }).click()
    await expect(this.item(title)).toBeVisible()
  }

  async start(title: string): Promise<void> {
    await this.page.getByRole('button', { name: `Move ${title} into Discovery` }).click()
    await expect(this.ticketTitled(title)).toBeVisible()
  }

  async moveToBacklog(ticket: string): Promise<void> {
    await card(this.page, ticket).locator('.card-moves .card-move').first().click()
    await expect(card(this.page, ticket)).toHaveCount(0)
  }

  async textOf(title: string): Promise<string> {
    await this.item(title).locator('.card-hit').click()
    return this.page.locator('.item-text').innerText()
  }

  async isInBacklog(title: string): Promise<boolean> {
    return (await this.item(title).count()) > 0
  }

  async columnOfTicket(title: string): Promise<string> {
    return (await this.ticketTitled(title).locator('xpath=ancestor::*[@data-column][1]').getAttribute('data-column')) ?? ''
  }

  async stateOfWork(title: string, fidelity: string): Promise<string> {
    const skill = fidelity.replace('stories-', 'stories-stories-').replaceAll('_', '-')
    const label = await this.ticketTitled(title).getByRole('button', { name: new RegExp(`${skill}: `) }).getAttribute('aria-label')
    return STATE_WORDS[label?.split(': ')[1] ?? ''] ?? ''
  }
}
