/**
 * Drags and reads what a person drags and reads. The Playwright and e2e tiers share it, so the same steps run
 * against the examples and against the whole stack.
 */
import { expect, type Locator, type Page } from '@playwright/test'

import { BY_ITS_TITLE, card, openBoard, turnOffActiveSessionOnly } from '../../support'
import type { MoveTicketDriver, TicketPlace } from './move_ticket.spec.shared'

const STAGES = ['Discovery', 'Specification', 'Implementation']

// Read in one step on the page, because the card can leave the board between two separate reads.
function placeOnPage(ticket: string): TicketPlace | null {
  const shown = document.querySelector(`.ticket-card[data-ticket="${ticket}"]`)
  if (!shown) return null
  const list = shown.closest('.card-list')?.querySelector('.list-label')?.textContent
  return { column: shown.closest('[data-column]')?.getAttribute('data-column') ?? '', isDone: list === 'DONE' }
}

// One step on, as a person drags it: In progress to Done, then into the next stage, then past Implementation into Complete.
function nextPlace({ column, isDone }: TicketPlace): TicketPlace {
  if (!isDone) return { column, isDone: true }
  const following = STAGES[STAGES.indexOf(column) + 1]
  return following ? { column: following, isDone: false } : { column: 'Complete', isDone: false }
}

// One step back: Done to In progress, In progress to the previous stage's Done, Discovery to the Backlog, Complete to Implementation's Done.
function previousPlace({ column, isDone }: TicketPlace): TicketPlace {
  if (column === 'Complete') return { column: 'Implementation', isDone: true }
  if (isDone) return { column, isDone: false }
  const earlier = STAGES[STAGES.indexOf(column) - 1]
  return earlier ? { column: earlier, isDone: true } : { column: 'Backlog', isDone: false }
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

  private whereIs(ticket: string): Promise<TicketPlace | null> {
    return this.page.evaluate(placeOnPage, ticket)
  }

  // A stage has an In progress and a Done list; the Backlog and Complete have one.
  private listAt({ column, isDone }: TicketPlace): Locator {
    const lists = this.page.locator(`[data-column="${column}"] .card-list`)
    return STAGES.includes(column) && isDone ? lists.nth(1) : lists.first()
  }

  // The page reads the board again after a drop, so a step ends once the card has moved.
  private async drag(ticket: string, target: (place: TicketPlace) => TicketPlace): Promise<void> {
    const before = (await this.whereIs(ticket))!
    await card(this.page, ticket).dragTo(this.listAt(target(before)), { sourcePosition: BY_ITS_TITLE })
    await expect.poll(() => this.whereIs(ticket)).not.toEqual(before)
  }

  moveNext(ticket: string): Promise<void> {
    return this.drag(ticket, nextPlace)
  }

  movePrevious(ticket: string): Promise<void> {
    return this.drag(ticket, previousPlace)
  }

  dragTo(ticket: string, stage: string, done: boolean): Promise<void> {
    return this.drag(ticket, () => ({ column: stage, isDone: done }))
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
