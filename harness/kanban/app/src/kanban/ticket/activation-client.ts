import { TicketClientGenerated, type WorkspaceData } from '@cdd/harness/kanban/ticket'

import type { BoardPage } from '../board/board-page'
import type { Activation } from '../board/board-store'
import type { TicketClient } from './ticket-client'
import { WorkspaceClient } from './workspace-client'

const FIRST_LEAVING = ['commit', 'push']
const LEFT_STEPS: Record<string, string> = { commit: 'committed', push: 'pushed', merge: 'merged to main' }
const OPENED_STEPS: Record<string, string> = { branch: 'branch created', worktree: 'worktree created' }
const NO_WORKSPACE: WorkspaceData = { has_branch: false, has_worktree: false, leaving_has_branch: false }

const toggled = (chosen: string[], option: string): string[] => (chosen.includes(option) ? chosen.filter(entry => entry !== option) : [...chosen, option])

const stepsOf = (steps: Record<string, string>, chosen: string[]): string[] =>
  Object.keys(steps)
    .filter(step => chosen.includes(step))
    .map(step => steps[step] ?? step)

// What leaving did, in the canvas's words, ahead of what came of the session.
function reportOf(open: Activation, outcome: string, opened: string[]): string {
  const left = stepsOf(LEFT_STEPS, open.leaving)
  return [left.length ? `${open.leavingTitle}: ${left.join(', ')}` : '', opened.length ? `${open.title}: ${opened.join(', ')}` : '', outcome].filter(Boolean).join(' · ')
}

export const activationHeading = (open: Activation): string => {
  if (open.isClosing) return `Close session ${open.title}`
  return open.leavingTitle ? `Switch from ${open.leavingTitle} to ${open.title}` : `Activate ${open.title}`
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
    const found = await ticket.workspace()
    const workspace = new WorkspaceClient(found ?? NO_WORKSPACE)
    const leavingTitle = isClosing ? ticket.title : (this.page.board.activeTicket?.title ?? '')
    this.show({
      ticket: ticket.name,
      title: ticket.title,
      isClosing,
      leavingTitle,
      leaving: workspace.leavingHasBranch ? FIRST_LEAVING : [],
      opening: workspace.hasBranch ? [] : ['branch'],
      workspace,
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
    const closed = await TicketClientGenerated.named(this.page.api, open.ticket).close(open.leaving)
    await this.page.reader.refresh()
    if (!closed) return
    this.page.ticket(closed.toJSON()).select()
    this.page.store.toast(reportOf(open, `Session ${open.title} closed`, []))
  }

  private async activateSession(open: Activation): Promise<void> {
    const activated = await TicketClientGenerated.named(this.page.api, open.ticket).activate(open.leaving, open.opening)
    await this.page.reader.refresh()
    if (activated) this.page.store.toast(reportOf(open, `${open.title} is now active`, stepsOf(OPENED_STEPS, open.opening)))
  }
}
