import { FidelityProgressClientGenerated, type FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'

import { STATES, WORK_LIGHT } from '../board/board-brand'
import type { TicketClient } from './ticket-client'

export type ProgressLook = { label: string; color: string; key: string }

// One fidelity's progress on a ticket as the page knows it: the Python FidelityProgress's own data and tools, and how a
// tile and a card segment draw it. It is made from the ticket that holds it, so it can say whether it is the ticket's next.
export class FidelityProgressClient extends FidelityProgressClientGenerated {
  constructor(
    json: FidelityProgressData,
    private readonly holder: TicketClient,
  ) {
    super(holder.api, json)
  }

  // Its state in the words and colour the board shows.
  get look(): ProgressLook {
    return { ...STATES[this.state]!, key: this.state }
  }

  // A fidelity whose practice the ticket's session has turned off is drawn faint.
  get light(): number {
    return this.isEnabled ? WORK_LIGHT[this.state]! : WORK_LIGHT.off!
  }

  // Python says which actions have something to work on; the page adds no rule of its own.
  allows(action: string): boolean {
    return this.allowedActions.includes(action)
  }

  get isNext(): boolean {
    return this.holder.next?.slug === this.slug
  }
}
