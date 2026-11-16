import type { BoardPage } from '../board/board-page'
import type { TicketClient } from './ticket-client'

// The step Run next takes on a ticket: the next fidelity's own next action, sent to the ticket's chat.
export class TicketNextStep {
  constructor(
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  // The action Run next sends: the next fidelity's own next action.
  get action(): string {
    return this.ticket.work.nextProgress?.nextAction ?? ''
  }

  get canRun(): boolean {
    if (!this.ticket.next || this.ticket.isLocked) return false
    // Opening the report while violations hold the fidelity is done on the board, so it needs no chat.
    return this.ticket.work.nextProgress?.state === 'violations' || this.page.chat.canSend
  }

  // Python gives the command for the next action, naming the session and no format. Generate is sent straight to the
  // chat, in the format the fidelity keeps; the others fill the prompt. While violations hold the fidelity, Run next opens
  // its report on the board, where the person reads them and sends the fix.
  async run(): Promise<void> {
    const next = this.ticket.work.nextProgress
    if (!next) return
    if (next.state === 'violations') return this.page.panels.openReport(this.ticket, next)
    const command = next.commands[this.action] ?? ''
    if (this.action !== 'generate') return this.ticket.chat.fill(command)
    await this.ticket.chat.command(command)
  }
}
