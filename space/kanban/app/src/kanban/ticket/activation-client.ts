import type { BoardPage } from '../board/board-page'
import type { Activation } from '../shared/board-store'
import type { TicketClient } from './ticket-client'

const LEFT_STEPS: Record<string, string> = { handoff: 'handoff written', commit: 'committed', push: 'pushed', merge: 'merged to main' }
const OPENED_STEPS: Record<string, string> = { branch: 'branch created', worktree: 'worktree created' }

const toggled = (chosen: string[], option: string): string[] => (chosen.includes(option) ? chosen.filter(entry => entry !== option) : [...chosen, option])

const stepsOf = (steps: Record<string, string>, chosen: string[]): string[] =>
  Object.keys(steps)
    .filter(step => chosen.includes(step))
    .map(step => steps[step] ?? step)

// What leaving did, in the canvas's words, ahead of what came of the session.
function reportOf(open: Activation, outcome: string, opened: string[]): string {
  const left = stepsOf(LEFT_STEPS, open.leaving)
  return [left.length ? `${open.leavingTitle}: ${left.join(', ')}` : '', opened.length ? `${open.ticket.title}: ${opened.join(', ')}` : '', outcome].filter(Boolean).join(' · ')
}

export const activationHeading = (open: Activation): string => {
  const { title } = open.ticket
  if (open.isClosing) return `Close session ${title}`
  return open.leavingTitle ? `Switch from ${open.leavingTitle} to ${title}` : `Activate ${title}`
}

// The dialog asked before the session changes, because leaving can commit, push, and merge work.
export class ActivationClient {
  constructor(private readonly page: BoardPage) {}

  private get open(): Activation | null {
    return this.page.store.state.activation
  }

  private show(activation: Activation | null): void {
    this.page.store.change({ activation })
  }

  async start(ticket: TicketClient, isClosing: boolean): Promise<void> {
    ticket.select()
    const left = isClosing ? ticket : this.page.board.activeTicket
    // Python says what leaving the ticket left can do with its work now, closing it or switching away, and what opening
    // this one can create now, with those chosen at first. A read that failed offers nothing, since the page has shown
    // the failure.
    const [opening, leaving] = await Promise.all([ticket.openChoices(), left ? (isClosing ? left.closeChoices() : left.leaveChoices()) : null])
    this.show({
      ticket,
      isClosing,
      leavingTitle: left?.title ?? '',
      leaving: leaving?.chosen ?? [],
      opening: opening?.choices ?? [],
      offeredLeaving: leaving?.choices ?? [],
      offeredOpening: opening?.choices ?? [],
      leavingBranch: leaving?.branch ?? '',
      hasBranch: opening?.has_branch ?? false,
    })
  }

  cancel(): void {
    this.show(null)
  }

  toggleLeaving(option: string): void {
    if (this.open) this.show({ ...this.open, leaving: toggled(this.open.leaving, option) })
  }

  toggleOpening(option: string): void {
    if (this.open) this.show({ ...this.open, opening: toggled(this.open.opening, option) })
  }

  async confirm(): Promise<void> {
    const open = this.open
    if (!open) return
    this.show(null)
    await (open.isClosing ? this.closeSession(open) : this.activateSession(open))
  }

  private async closeSession(open: Activation): Promise<void> {
    const closed = await open.ticket.close(open.leaving)
    await this.page.reader.refresh()
    if (!closed) return
    this.page.ticket(closed.toJSON()).select()
    this.page.store.toast(reportOf(open, `Session ${open.ticket.title} closed`, []))
  }

  private async activateSession(open: Activation): Promise<void> {
    const activated = await open.ticket.activate(open.leaving, open.opening)
    await this.page.reader.refresh()
    if (activated) this.page.store.toast(reportOf(open, `${open.ticket.title} is now active`, stepsOf(OPENED_STEPS, open.opening)))
  }
}
