import type { BoardFidelityData, PracticeGuidanceData } from '@cdd/space/kanban/board'

// A practice as the board shows it: its name and colour, and its fidelities, which Python sends each with its practice,
// so the page finds a fidelity's practice without taking the slug apart.
export class PracticeClient {
  constructor(
    private readonly guidance: PracticeGuidanceData,
    private readonly fidelities: BoardFidelityData[],
  ) {}

  get key(): string {
    return this.guidance.key
  }

  get slug(): string {
    return this.guidance.slug
  }

  get name(): string {
    return this.guidance.short_name
  }

  get color(): string {
    return this.guidance.colour
  }

  has(slug: string): boolean {
    return this.fidelities.some(shown => shown.fidelity.slug === slug)
  }
}
