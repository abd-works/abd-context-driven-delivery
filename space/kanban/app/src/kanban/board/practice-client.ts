import type { PracticeGuidanceData } from '@cdd/space/kanban/board'

// A practice as the board shows it. Python sends every practice with its name, its colour, and its fidelities' slugs,
// so the page looks a fidelity's practice up rather than taking the slug apart.
export class PracticeClient {
  constructor(private readonly data: PracticeGuidanceData) {}

  get key(): string {
    return this.data.key
  }

  get slug(): string {
    return this.data.slug
  }

  get name(): string {
    return this.data.short_name
  }

  get color(): string {
    return this.data.colour
  }

  has(slug: string): boolean {
    return this.data.fidelities.includes(slug)
  }
}
