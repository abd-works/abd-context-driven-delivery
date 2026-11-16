
import type { ColumnOverviewData } from '@cdd/space/kanban/board'


// One glyph for each column board.overview sends, standing for the canvas's icons: Backlog, Discovery (magnifier),
// Specification (document), Implementation (gear), Complete (check). A column the canvas has no icon for shows a dot.
const STAGE_ICONS: Record<string, string> = { Backlog: '☰', Discovery: '⌕', Specification: '▤', Implementation: '⚙', Complete: '✓' }

export function stageIconOf(stage: string): string {
  return STAGE_ICONS[stage] ?? '·'
}

const INK = '#E5531A'
const FAINT_INK = '#E5531A66'
// A shown stage that is not the session's own gets the canvas's orange tint instead of an underline.
const TINT = '#E5531A2E'

// One column of the board as board.overview sends it, placed against the active session's column: how many columns
// past the session's it is, below zero for the columns behind the session, above zero for the ones not yet reached.
export class StageClient {
  constructor(
    readonly column: ColumnOverviewData,
    private readonly columnsPastSession: number,
    readonly isShown: boolean,
  ) {}

  get stage(): string {
    return this.column.name
  }

  // The column the active session is in, which the line underlines.
  get isCurrent(): boolean {
    return this.columnsPastSession === 0
  }

  // Only a stage requires fidelities, so the Backlog and Complete have none to show.
  get canShow(): boolean {
    return this.column.kind === 'stage'
  }

  get icon(): string {
    return stageIconOf(this.column.name)
  }

  // Stages not yet reached are faint, so the path still reads left to right.
  get ink(): string {
    return this.columnsPastSession > 0 ? FAINT_INK : INK
  }

  // What the stage is for, as its column's scope sends it, which the canvas shows on hover beside its name, such as
  // whole solution · wide / shallow. The Backlog and Complete have no scope.
  get scope(): string {
    const scope = this.column.scope
    return scope ? `${scope.name.toLowerCase()} · ${scope.reach}` : ''
  }

  // A stage shown in place of the session's own reads tinted; only the session's own is underlined.
  get tint(): string | undefined {
    return this.isShown ? TINT : undefined
  }
}
