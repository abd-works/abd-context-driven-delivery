import type { BoardPage } from '../board/board-page'
import type { Closing } from '../shared/board-store'
import type { TicketClient } from './ticket-client'

const LEFT_STEPS: Record<string, string> = { handoff: 'handoff written', commit: 'committed', push: 'pushed', merge: 'merged to main', delete_branch: 'branch deleted', delete_worktree: 'worktree deleted' }

const toggled = (chosen: string[], option: string): string[] => (chosen.includes(option) ? chosen.filter(entry => entry !== option) : [...chosen, option])

// What closing did with the work, in the canvas's words, ahead of the session closed.
function closedReport(closing: Closing): string {
  const left = Object.keys(LEFT_STEPS)
    .filter(step => closing.leaving.includes(step))
    .map(step => LEFT_STEPS[step] ?? step)
  return [left.length ? `${closing.ticket.title}: ${left.join(', ')}` : '', `Session ${closing.ticket.title} closed`].filter(Boolean).join(' · ')
}

export const closingHeading = (closing: Closing): string => `Close session ${closing.ticket.title}`

// Activating a ticket opens it in its own worktree in one press, since it changes nothing the chats have open. Closing
// asks first, in a dialog, because it can commit, push, and merge the ticket's work.
export class ActivationClient {
  constructor(private readonly page: BoardPage) {}

  private get closing(): Closing | null {
    return this.page.store.state.closing
  }

  private show(closing: Closing | null): void {
    this.page.store.change({ closing })
  }

  // The board then sends the person to the chat working in that worktree, or, with none working there yet, starts one
  // there, so the person is left with the ticket's chat either way.
  async activate(ticket: TicketClient): Promise<void> {
    ticket.select()
    const activated = await ticket.activate()
    await this.page.reader.refresh()
    if (!activated) return
    const opened = this.page.ticket(activated.toJSON())
    opened.choose()
    if (!opened.chat.found) return opened.openChat()
    this.page.store.toast(`${opened.title} is open in its worktree ${opened.worktree} · its chat is chosen`)
  }

  // Python says what closing the ticket can do with its work now, with those chosen at first. A read that failed
  // offers nothing, since the page has shown the failure.
  async startClosing(ticket: TicketClient): Promise<void> {
    ticket.select()
    const choices = await ticket.closeChoices()
    this.show({ ticket, leaving: choices?.chosen ?? [], offeredLeaving: choices?.choices ?? [], leavingBranch: choices?.branch ?? '' })
  }

  cancel(): void {
    this.show(null)
  }

  toggleLeaving(option: string): void {
    if (this.closing) this.show({ ...this.closing, leaving: toggled(this.closing.leaving, option) })
  }

  async confirm(): Promise<void> {
    const closing = this.closing
    if (!closing) return
    this.show(null)
    const closed = await closing.ticket.close(closing.leaving)
    await this.page.reader.refresh()
    if (!closed) return
    this.page.ticket(closed.toJSON()).select()
    this.page.store.toast(closedReport(closing))
  }
}
