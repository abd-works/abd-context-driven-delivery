// Model shell for one fidelity dot of the chat bar and its actions (patterns-cdd-claude-mod).
import type { EngineInterface } from 'claude-code'

// A practice fidelity of the shown stage, shaded by status as on the board.
export class FidelityClient {
  declare readonly fidelity: string
  declare readonly status: string // generate, validate, review, reviewed, violations: TicketData.progress
  declare readonly violationCount: number
  declare readonly isSelected: boolean
  declare readonly nextAction: string // the action button's icon for this fidelity
}

// Atom selectedFidelity, declared in pane/types/index.d.ts and kept in this file. Actions run on it alone.
export function currentFidelity($: EngineInterface): string | null { return null }

export async function selectFidelity($: EngineInterface, fidelity: FidelityClient): Promise<void> {} // atom only
export async function runAction($: EngineInterface, fidelity: FidelityClient, action: string): Promise<void> {} // -> ticket.generate_commands, then $.command.run
export async function reviewFidelity($: EngineInterface, fidelity: FidelityClient): Promise<void> {} // -> ticket.finish_review
export async function openFiles($: EngineInterface, fidelity: FidelityClient): Promise<void> {} // -> ticket.files, ticket.read_file
export async function openBoard($: EngineInterface, fidelity: FidelityClient): Promise<void> {} // $.command.run /board
