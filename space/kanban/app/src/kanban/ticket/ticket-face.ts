import type { TicketClient } from './ticket-client'

// What the page writes about a ticket: where it stands, where it came from, and what Run next will do, in the words its
// card, details, and panels show.
export class TicketFace {
  constructor(private readonly ticket: TicketClient) {}

  get standing(): string {
    return this.ticket.isClosed ? '' : this.ticket.isDone ? 'done' : 'in progress'
  }

  // Where a split ticket came from: `story of epic`.
  get origin(): string {
    const { scope, parent } = this.ticket.session
    return scope && parent ? `${scope} of ${parent}` : scope
  }

  get stagePlace(): string {
    return [this.ticket.column.name, this.standing].filter(Boolean).join(' · ')
  }

  get runNextLabel(): string {
    return this.ticket.next ? `Run next: ${this.ticket.nextStep.action}` : 'Run next'
  }

  // The run-next icon's tooltip names the step and the fidelity it runs on, since the icon itself cannot.
  get runNextHint(): string {
    if (this.ticket.isLocked) return 'Activate this session to run its next step'
    if (!this.ticket.next) return 'Nothing to run next'
    return `${this.runNextLabel} on ${this.ticket.next.fidelity.slug}`
  }

  get nextNote(): string {
    const { next } = this.ticket
    return next ? `Next: ${next.fidelity.slug}, ${this.ticket.nextStep.action}` : ''
  }

  get lockNote(): string {
    return this.ticket.isLocked ? 'Activate this session to run actions' : ''
  }
}
