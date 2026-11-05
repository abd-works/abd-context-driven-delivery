// Model shell for one stage icon of the chat bar and its action (patterns-cdd-claude-mod).
import type { EngineInterface } from 'claude-code'

// Backlog, Discovery, Specification, Implementation, or Complete.
export class StageClient {
  declare readonly stage: string
  declare readonly status: string // done, in progress, not reached
  declare readonly isShown: boolean
}

// Atom shownStage, declared in pane/types/index.d.ts and kept in this file: the stage whose fidelities the dots show.
export function currentStage($: EngineInterface): string | null { return null }

export async function selectStage($: EngineInterface, stage: StageClient): Promise<void> {} // atom only
