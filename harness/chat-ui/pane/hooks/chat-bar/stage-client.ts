import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

const shownStage = atom({ plugin: 'cdd-board', key: 'shownStage' } as const, null as string | null)

// One glyph per stage, standing for the canvas's icons: Backlog, Discovery (magnifier), Specification (document),
// Implementation (gear), Complete (check).
const STAGE_ICONS: Record<string, string> = { Backlog: '☰', Discovery: '⌕', Specification: '▤', Implementation: '⚙', Complete: '✓' }
const INK = '#E5531A'
const FAINT_INK = '#E5531A66'

export type StageJson = { name: string; status: 'done' | 'in_progress' | 'not_reached'; isShown: boolean; canShow: boolean }

// Backlog, Discovery, Specification, Implementation, or Complete.
export class StageClient {
  constructor(private readonly json: StageJson) {}

  get stage(): string {
    return this.json.name
  }

  get status(): StageJson['status'] {
    return this.json.status
  }

  get isShown(): boolean {
    return this.json.isShown
  }

  // Backlog and Complete hold no fidelities, so only the three working stages can be shown.
  get canShow(): boolean {
    return this.json.canShow
  }

  get icon(): string {
    return STAGE_ICONS[this.json.name] ?? '·'
  }

  // Stages not yet reached are faint, so the path still reads left to right.
  get ink(): string {
    return this.json.status === 'not_reached' ? FAINT_INK : INK
  }
}

// Atom shownStage, declared in pane/types/index.d.ts and kept in this file: the stage whose fidelities the dots show.
export function shownStageName($: EngineInterface) {
  return read($, shownStage)
}

// Showing the stage in progress goes back to it. A fidelity of the last stage then reads as none selected, because
// ChatBarClient.selectedFidelity looks only among the shown stage's fidelities.
export async function selectStage($: EngineInterface, stage: StageClient): Promise<void> {
  if (!stage.canShow) return
  await update($, shownStage, () => (stage.status === 'in_progress' ? null : stage.stage))
}
