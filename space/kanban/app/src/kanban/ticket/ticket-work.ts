import type { RequiredFidelity } from '../board/column-client'
import type { FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import type { StageWorkData } from '@cdd/space/kanban/ticket'

import type { BoardPage } from '../board/board-page'
import type { ColumnClient } from '../board/column-client'
import { FidelityProgressClient } from './fidelity-progress-client'
import { ReportClient } from './report-client'
import type { TicketClient } from './ticket-client'

// A ticket's progress on each fidelity the board requires, as the page knows it: each fidelity's progress answers its own
// tools, and the reports a tile or panel over several of them reads side by side.
export class TicketWork {
  constructor(
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  get violatedSlugs(): string[] {
    return this.ticket.progress.filter(progress => progress.state === 'violations').map(progress => progress.fidelity.slug)
  }

  // Its progress on every fidelity the board requires, in stage order, each answering its own tools: made once for the
  // progress it was read with, and again only when one of its own tools has brought the ticket a new reading.
  get fidelityProgress(): FidelityProgressClient[] {
    const read = this.ticket.progress
    if (this.heldProgress?.read !== read) this.heldProgress = { read, clients: read.map(progress => new FidelityProgressClient(progress, this.ticket)) }
    return this.heldProgress.clients
  }

  private heldProgress: { read: FidelityProgressData[]; clients: FidelityProgressClient[] } | null = null

  // Its progress on the fidelities of a stage whose practices its session works on, in the order the stage requires them.
  progressIn(stage: ColumnClient): FidelityProgressClient[] {
    return this.fidelityProgress.filter(progress => progress.stage.name === stage.name && progress.isEnabled)
  }

  // Its progress on the fidelities a tile or a panel was opened over, read from this ticket as it is now.
  progressOn(fidelities: RequiredFidelity[]): FidelityProgressClient[] {
    return fidelities.flatMap(fidelity => this.progressNamed(fidelity.slug) ?? [])
  }

  // The data names a fidelity's progress by its slug, such as the ticket's next or a report rule's fidelity; this is
  // the one place such a name is turned into the progress.
  progressNamed(slug: string): FidelityProgressClient | undefined {
    return this.fidelityProgress.find(progress => progress.fidelity.slug === slug)
  }

  // The progress Run next works on: the one the ticket names as its next, none when it is done in its stage.
  get nextProgress(): FidelityProgressClient | undefined {
    return this.ticket.next ? this.progressNamed(this.ticket.next.fidelity.slug) : undefined
  }

  // Its work in a stage taken together, as Python sends it (StageWork), which a stage head's action bar shows and acts on.
  workIn(stage: ColumnClient): StageWorkData | undefined {
    return this.ticket.stageWork.find(entry => entry.stage.name === stage.name)
  }

  // One fidelity's latest report, or with none the violations of every fidelity of the ticket's stage.
  async reportOf(progress: FidelityProgressClient | null): Promise<ReportClient | null> {
    const report = await (progress ? progress.report() : this.ticket.violations())
    return report ? new ReportClient(report, this.ticket, this.page) : null
  }
}
