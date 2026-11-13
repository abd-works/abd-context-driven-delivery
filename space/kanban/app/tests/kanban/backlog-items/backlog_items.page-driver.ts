/**
 * Presses and reads what a person presses and reads. The Playwright and e2e tiers share it, so the same steps run
 * against the examples and against the whole stack.
 */
import { expect, type Locator, type Page } from '@playwright/test'

import { card, catchClaudeLinks, dragCard, openBoard, toast, turnOffActiveSessionOnly } from '../../support'
import type { BacklogItemsDriver } from './backlog_items.spec.shared'

// A segment names its skill and the state of that fidelity's work, as `/practices-stories-stories-story-map: in progress`.
const STATE_WORDS: Record<string, string> = { 'in progress': 'in_progress', 'not started': 'not_started', done: 'done', violations: 'violations' }

export class BacklogItemsPageDriver implements BacklogItemsDriver {
  private readonly page: Page

  private constructor(page: Page) {
    this.page = page
  }

  // Starting an item starts its chat; the link is caught, so a run opens no real chat in the Claude app.
  static async fromPage(page: Page): Promise<BacklogItemsPageDriver> {
    await catchClaudeLinks(page)
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

  // A person starts an item by dragging it into Discovery's In progress, then chooses the folder its session works in.
  async start(title: string): Promise<void> {
    await dragCard(this.page, this.item(title), this.page.locator('[data-column="Discovery"] .card-list').first())
    const roots = this.page.getByRole('dialog')
    await roots.getByRole('button', { name: 'Use whole repository' }).click()
    // Starting opens the ticket's worktree and its chat in the background; the next scenario's reset must wait for it.
    await expect(toast(this.page, /^Confirm the folder and send in the Claude app/)).toBeVisible({ timeout: 15_000 })
    await roots.getByRole('button', { name: 'Done' }).click()
    await expect(this.ticketTitled(title)).toBeVisible()
  }

  async moveToBacklog(ticket: string): Promise<void> {
    await dragCard(this.page, card(this.page, ticket), this.page.locator('[data-column="Backlog"] .card-list'))
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
