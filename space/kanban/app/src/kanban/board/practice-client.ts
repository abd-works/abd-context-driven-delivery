import type { BoardFidelityData, PracticeGuidanceData } from '@cdd/space/kanban/board'

// A practice as the board shows it: its name and colour, and its fidelities, which Python sends each with its practice,
// so the page finds a fidelity's practice without taking the slug apart.
export class PracticeClient {
  constructor(
    private readonly data: PracticeGuidanceData,
    private readonly fidelities: BoardFidelityData[],
  ) {}

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
    return this.fidelities.some(shown => shown.fidelity.slug === slug)
  }
}
