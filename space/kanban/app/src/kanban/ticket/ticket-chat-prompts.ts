import type { BoardPage } from '../board/board-page'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { TicketClient } from './ticket-client'

const CLOSE_SESSION_COMMAND = '/space:session:close-session'

// What a ticket asks its chat to do for it: split it, write its handoff, close its session, or validate a fidelity
// again. Each goes to the ticket's own chat and names the ticket's session.
export class TicketChatPrompts {
  constructor(
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  // A prompt runs in whichever chat it is sent to, whose open session can be another ticket's, so a prompt for this
  // ticket, such as a report's fix, names this ticket's session.json, as Python's action commands do.
  inSession(prompt: string): string {
    return `${prompt} session=${this.ticket.session.session_file}`
  }

  fillSplit(): Promise<void> {
    const name = this.ticket.name
    return this.ticket.chat.fill(this.inSession(`Split ticket ${name} into child tickets, one per story on its story map: call ticket.create with parent ${name} for each story.`))
  }

  // Closing ends the chat's session and leaves the ticket where it is; moving it into Complete is what completes it.
  closeSession(): Promise<void> {
    return this.ticket.chat.command(this.inSession(CLOSE_SESSION_COMMAND))
  }

  get closeHint(): string {
    return this.closesInChat ? 'Close this session in the chat' : 'Close this ticket and choose what to do with its work'
  }

  startClose(): Promise<void> {
    return this.closesInChat ? this.closeSession() : this.page.activation.startClosing(this.ticket)
  }

  fillHandoff(): Promise<void> {
    return this.ticket.chat.fill(this.inSession(`Write a handoff for ticket ${this.ticket.name} with /space-session-handoff-session`))
  }

  // A report whose saved graph is out of date has lost its graph's rules, so its fidelity is validated again to find them.
  validateAgain(progress: FidelityProgressClient): Promise<void> {
    return this.ticket.chat.command(progress.commands.validate ?? '')
  }

  // An open ticket closes in the chosen chat when that chat works on it, so the agent can write its handoff; any other
  // open ticket, such as one in its worktree with no chat chosen, closes through the board's Close dialog.
  private get closesInChat(): boolean {
    return this.ticket.isActive && this.page.chat.canSend
  }
}
