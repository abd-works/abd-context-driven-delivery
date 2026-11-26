import { PracticeSessionOutputClientGenerated } from '@cdd/space/session/practices/practice-session-output'

import type { BoardPage } from '../board/board-page'
import type { TicketClient } from './ticket-client'

// The practices a ticket's session works on, as Python sends them with the ticket: each answers its own tools, and a
// person turns one on or off from the ticket.
export class TicketPractices {
  constructor(
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  client(practice: string): PracticeSessionOutputClientGenerated {
    return new PracticeSessionOutputClientGenerated(this.ticket.api, this.ticket.session.practices[practice] ?? null)
  }

  // Python sends every practice of the ticket's session with whether it works on it.
  isOn(practice: string): boolean {
    return this.ticket.session.practices[practice]?.enabled === true
  }

  async enable(practice: string, isEnabled: boolean): Promise<boolean> {
    const saved = await this.client(practice).enable(isEnabled)
    await this.page.reader.refresh()
    if (!saved) return false
    if (!isEnabled) this.page.cards.dropPractice(this.ticket, practice)
    const name = this.page.board.practiceNamed(practice)?.name ?? practice
    this.page.store.toast(`${name} ${isEnabled ? 'on' : 'off'} for ${this.ticket.title} · saved to ${this.ticket.session.session_file}`)
    return true
  }
}
