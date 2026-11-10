import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ColumnOverviewData } from '@cdd/space/kanban/board'

import { clearChosenAction } from './action-picker-client'

const shownStage = atom({ plugin: 'cdd-board', key: 'shownStage' } as const, null as string | null)
// Atom stagePicker, declared in pane/types/index.d.ts: whether the stage button's list is open.
const stagePicker = atom({ plugin: 'cdd-board', key: 'stagePicker' } as const, false)

export function isStagePickerOpen($: EngineInterface) {
  return read($, stagePicker)
}

export async function toggleStagePicker($: EngineInterface): Promise<void> {
  await update($, stagePicker, isOpen => !isOpen)
}

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

// One column of the board as board.overview sends it, placed against the active session's column: the columns before it
// are behind the session, the ones after it not yet reached.
export class StageClient {
  constructor(
    readonly column: ColumnOverviewData,
    private readonly place: number,
    private readonly sessionPlace: number,
    readonly isShown: boolean,
  ) {}

  get stage(): string {
    return this.column.name
  }

  // The column the active session is in, which the line underlines.
  get isCurrent(): boolean {
    return this.place === this.sessionPlace
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
    return this.place > this.sessionPlace ? FAINT_INK : INK
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

// Atom shownStage, declared in pane/types/index.d.ts and kept in this file: the stage whose fidelities the dots show.
export function shownStageName($: EngineInterface) {
  return read($, shownStage)
}

// Showing the session's own stage goes back to it. A fidelity of the last stage then reads as none selected, because
// ChatBarClient.selectedFidelity looks only among the shown stage's fidelities.
// Showing another stage drops an action picked from the menu, so the button shows the shown stage's next action.
export async function selectStage($: EngineInterface, stage: StageClient): Promise<void> {
  if (!stage.canShow) return
  await update($, shownStage, () => (stage.isCurrent ? null : stage.stage))
  await update($, stagePicker, () => false)
  await clearChosenAction($)
}
