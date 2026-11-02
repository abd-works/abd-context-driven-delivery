/**
 * Presses and reads what a person presses and reads. The Playwright and e2e tiers share it, so the same steps run
 * against the examples and against the whole stack.
 */
import { expect, type Locator, type Page } from '@playwright/test'

import { card, openBoard, turnOffActiveSessionOnly } from '../../support'
import type { MoveTicketDriver, TicketPlace } from './move_ticket.spec.shared'

// Read in one step on the page, because the card can leave the board between two separate reads.
function placeOnPage(ticket: string): TicketPlace | null {
  const shown = document.querySelector(`.ticket-card[data-ticket="${ticket}"]`)
  if (!shown) return null
  const list = shown.closest('.card-list')?.querySelector('.list-label')?.textContent
  return { column: shown.closest('[data-column]')?.getAttribute('data-column') ?? '', isDone: list === 'DONE' }
}

export class MoveTicketPageDriver implements MoveTicketDriver {
  private readonly page: Page

  private constructor(page: Page) {
    this.page = page
  }

  static async fromPage(page: Page): Promise<MoveTicketPageDriver> {
    await openBoard(page)
    await turnOffActiveSessionOnly(page)
    return new MoveTicketPageDriver(page)
  }

  private arrows(ticket: string): Locator {
    return card(this.page, ticket).locator('.card-moves .card-move')
  }

  private whereIs(ticket: string): Promise<TicketPlace | null> {
    return this.page.evaluate(placeOnPage, ticket)
  }

  // The page reads the board again after a press, so a step ends once the card has moved.
  private async press(ticket: string, arrow: Locator): Promise<void> {
    const before = await this.whereIs(ticket)
    await arrow.click()
    await expect.poll(() => this.whereIs(ticket)).not.toEqual(before)
  }

  moveNext(ticket: string): Promise<void> {
    return this.press(ticket, this.arrows(ticket).last())
  }

  movePrevious(ticket: string): Promise<void> {
    return this.press(ticket, this.arrows(ticket).first())
  }

  async placeOf(ticket: string): Promise<TicketPlace> {
    return (await this.whereIs(ticket))!
  }

  async isOnTheStages(ticket: string): Promise<boolean> {
    return (await card(this.page, ticket).count()) > 0
  }

  backlogTitles(): Promise<string[]> {
    return this.page.locator('.ticket-card[data-item] .ticket-title').allInnerTexts()
  }
}
