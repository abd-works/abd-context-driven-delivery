import type { BoardPage } from '../board/board-page'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { TicketClient } from './ticket-client'

// What a ticket asks its chat to do for it: split it, write its handoff, set up its roots, close its session, or validate
// a fidelity again. Each goes to the ticket's own chat in the words Python wrote (TicketPrompts), which name the
// ticket's session.
export class TicketChatPrompts {
  constructor(
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  fillSplit(): Promise<void> {
    return this.ticket.chat.fill(this.ticket.prompts.split)
  }

  // Closing ends the chat's session and leaves the ticket where it is; moving it into Complete is what completes it.
  closeSession(): Promise<void> {
    return this.ticket.chat.command(this.ticket.prompts.close_session)
  }

  get closeHint(): string {
    return this.closesInChat ? 'Close this session in the chat' : 'Close this ticket and choose what to do with its work'
  }

  startClose(): Promise<void> {
    return this.closesInChat ? this.closeSession() : this.page.activation.startClosing(this.ticket)
  }

  fillHandoff(): Promise<void> {
    return this.ticket.chat.fill(this.ticket.prompts.handoff)
  }

  // The chat proposes roots for the pieces the ticket works on, in every practice, and sets them once the person confirms.
  fillSetUpRoots(): Promise<void> {
    return this.ticket.chat.fill(this.ticket.prompts.set_up_roots)
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
