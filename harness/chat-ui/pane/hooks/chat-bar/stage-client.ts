import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ColumnOverviewData } from '@cdd/space/kanban/board'

import { post } from '../board-chat/board'
import { clearChosenAction } from './action-picker-client'

// The stages shown for the chat, as cdd holds them (chat.show_stages): the one choice the bar's stage buttons and a page
// the chat opened, such as the Files app, both show and change; null before either chose, when the bar starts the choice
// at the session's own stage. The atom only keeps what cdd last answered, for drawing.
const shownStages = atom({ plugin: 'cdd-board', key: 'shownStages' } as const, null as string[] | null)

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

// Atom shownStages, declared in pane/types/index.d.ts and kept in this file: the stages whose fidelities the dots show.
export async function shownStageNames($: EngineInterface): Promise<string[] | null> {
  return (await read($, shownStages)) ?? null
}

// The stages cdd holds for the chat, as chat.show or chat.show_stages answered them; a change from elsewhere, such as a
// stage pressed in the Files app, drops an action picked before.
export async function showStagesHeld($: EngineInterface, stages: string[] | null): Promise<void> {
  const held = await shownStageNames($)
  if (JSON.stringify(held) === JSON.stringify(stages)) return
  await update($, shownStages, () => stages)
  await clearChosenAction($)
}

// A press on a stage button shows that stage's fidelities beside those already shown, or no longer; the bar shows the
// stages cdd answers. With none left, none shows.
export async function toggleStage($: EngineInterface, shown: string[], stage: StageClient): Promise<void> {
  if (!stage.canShow) return
  const next = shown.includes(stage.stage) ? shown.filter(each => each !== stage.stage) : [...shown, stage.stage]
  // The button redraws at once; cdd's answer then replaces it.
  await showStagesHeld($, next)
  const answer = await post($, { chat: await $.session.id(), operation: 'show-stages', body: { shown_stages: next } })
  await showStagesHeld($, (JSON.parse(answer.text) as { shown_stages: string[] }).shown_stages)
}
