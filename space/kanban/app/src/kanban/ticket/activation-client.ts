import type { SessionChoicesData } from '@cdd/space/kanban/ticket'

import type { BoardPage } from '../board/board-page'
import type { Activation } from '../board/board-store'
import type { TicketClient } from './ticket-client'

const LEFT_STEPS: Record<string, string> = { handoff: 'handoff written', commit: 'committed', push: 'pushed', merge: 'merged to main' }
const OPENED_STEPS: Record<string, string> = { branch: 'branch created', worktree: 'worktree created' }
// A read that failed offers nothing, since the page has already shown the failure.
const nothingOn = (branch: string): SessionChoicesData => ({ branch: { name: branch, exists: false, is_checked_out: false }, choices: [] })

// What Python chooses to start with.
const chosenIn = (offered: SessionChoicesData | null): string[] => (offered?.choices ?? []).filter(choice => choice.is_chosen).map(choice => choice.name)

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
    const active = this.page.board.activeTicket
    // Python offers what leaving the active ticket can do with its work and what opening this one can create.
    const [openChoices, leaveChoices] = await Promise.all([ticket.openChoices(), active ? active.leaveChoices() : null])
    const leavingTitle = isClosing ? ticket.title : (active?.title ?? '')
    this.show({
      ticket,
      isClosing,
      leavingTitle,
      leaving: chosenIn(leaveChoices),
      opening: chosenIn(openChoices),
      leaveChoices,
      openChoices: openChoices ?? nothingOn(ticket.name),
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
