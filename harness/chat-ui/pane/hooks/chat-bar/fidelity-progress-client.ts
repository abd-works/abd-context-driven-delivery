import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { PracticeGuidanceData } from '@cdd/space/kanban/board'
import type { FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import type { TicketData } from '@cdd/space/kanban/ticket'

import { promptCommand } from '../shared/chat-command'
import { clearChosenAction } from './action-picker-client'

const selectedFidelity = atom({ plugin: 'cdd-board', key: 'selectedFidelity' } as const, null as string | null)

// The canvas's progress looks (design/StageStrip.dc.html), one for each state FidelityProgress.state sends; each
// practice's colour comes with the board.
const NO_PRACTICE_COLOUR = '#9B9BA8'
const LOOKS: Record<string, { mark: string; word: string; colour: string; shade: string }> = {
  not_started: { mark: '○', word: 'to do', colour: '#71717A', shade: '40' },
  in_progress: { mark: '…', word: 'doing', colour: '#F59E0B', shade: '80' },
  violations: { mark: '✕', word: 'violations', colour: '#EF4444', shade: 'FF' },
  done: { mark: '✓', word: 'done', colour: '#22C55E', shade: 'FF' },
}

// One fidelity's progress on the active session, as the Python FidelityProgress sends it, drawn as a dot of its
// practice's colour shaded by its state. It holds the progress itself and reads every answer from it.
export class FidelityProgressClient {
  constructor(
    readonly progress: FidelityProgressData,
    private readonly ticket: TicketData,
    private readonly practice: PracticeGuidanceData | undefined,
    readonly isSelected: boolean,
  ) {}

  // The fidelity's slug, such as ux-mockup: what names its progress to the fidelity-progress tools and its guidance to
  // the actions.
  get slug(): string {
    return this.progress.fidelity.slug
  }

  // The fidelity's own name as the session card shows it, such as Scenarios or Front end code.
  get name(): string {
    const words = this.progress.fidelity.name.replace(/_/g, ' ')
    return words.charAt(0).toUpperCase() + words.slice(1)
  }

  get word(): string {
    return this.progress.state === 'violations' ? `${this.violationCount} violations` : this.#look.word
  }

  // The state as FidelityProgress.state sends it: not_started, in_progress, violations or done.
  get state(): string {
    return this.progress.state
  }

  get mark(): string {
    return this.#look.mark
  }

  // The colour of the state's mark and word on the session card.
  get lookColour(): string {
    return this.#look.colour
  }

  get colour(): string {
    return this.practice?.colour || NO_PRACTICE_COLOUR
  }

  // The practice colour, fainter the less is done.
  get shade(): string {
    return `${this.colour}${this.#look.shade}`
  }

  get violationCount(): number {
    return this.progress.violation_count
  }

  // What the Python FidelityProgress names next: review while it has violations, since a person reads them and tells
  // the agent to fix them, else the first of generate, validate and review not done; nothing once it is done.
  get nextAction(): string {
    return this.progress.next_action
  }

  // The practice root this fidelity's files are written under, as the ticket's session holds it.
  get folder(): string {
    return this.ticket.session.practices[this.progress.practice.key]?.root ?? ''
  }

  // The command the Python FidelityProgress gives for action on this fidelity. It names the ticket's session, because the
  // chat that runs it can have another session open, and no format, so the action works in the format the fidelity keeps.
  commandFor(action: string): string {
    return this.progress.commands[action] ?? ''
  }

  get #look(): (typeof LOOKS)[string] {
    return LOOKS[this.progress.state] ?? LOOKS.not_started
  }
}

// Atom selectedFidelity, declared in pane/types/index.d.ts and kept in this file.
export function selectedFidelitySlug($: EngineInterface) {
  return read($, selectedFidelity)
}

// Selecting one fidelity replaces the last, so one dot is selected at most. Selecting another fidelity drops an action
// picked for the one before, so the button shows this one's next action.
export async function selectFidelity($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  await update($, selectedFidelity, () => fidelity.slug)
  await clearChosenAction($)
}

// The action's command goes in the prompt box for the person to send. Generate renders the earlier fidelity first
// itself when that fidelity has no file in the format, so every action is one command.
export async function runAction($: EngineInterface, fidelity: FidelityProgressClient, action: string): Promise<void> {
  await promptCommand($, fidelity.commandFor(action))
}
