import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { AppData } from '@cdd/harness/diagnostics/app'
import type { BoardPracticeData } from '@cdd/space/kanban/board'
import type { FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import type { TicketData } from '@cdd/space/kanban/ticket'

import { post } from '../board-chat/board'
import type { ChatBarClient } from './chat-bar-client'
import { clearChosenAction } from './action-picker-client'

// The canvas's progress looks (design/StageStrip.dc.html), one for each state FidelityProgress.state sends; each
// practice's colour comes with the board.
const NO_PRACTICE_COLOUR = '#9B9BA8'
const LOOKS: Record<string, { mark: string; word: string; colour: string; shade: string }> = {
  not_started: { mark: '○', word: 'to do', colour: '#71717A', shade: '40' },
  in_progress: { mark: '…', word: 'doing', colour: '#F59E0B', shade: '80' },
  violations: { mark: '✕', word: 'violations', colour: '#EF4444', shade: 'FF' },
  done: { mark: '✓', word: 'done', colour: '#22C55E', shade: 'FF' },
}

// Names too long for the session card's fidelity column, by the short form the card shows.
const SHORT_NAMES: Record<string, string> = { 'Information architecture': 'Info architecture' }

// One fidelity's progress on the active session, as the Python FidelityProgress sends it, drawn as a dot of its
// practice's colour shaded by its state. It holds the progress itself and reads every answer from it; the chat bar it
// is drawn on says how the board names it, its practice, and whether that practice is on.
export class FidelityProgressClient {
  constructor(
    readonly progress: FidelityProgressData,
    private readonly ticket: TicketData,
    private readonly chatBar: ChatBarClient,
  ) {}

  // Whether its practice is on for the session, so its dot is drawn selected.
  get isSelected(): boolean {
    return this.chatBar.isPracticeOn(this.progress.practice.key)
  }

  private get label(): string {
    return this.chatBar.labelOf(this.progress.fidelity.slug)
  }

  private get practice(): BoardPracticeData | undefined {
    return this.chatBar.practiceNamed(this.progress.practice.key)
  }

  // The fidelity's slug, such as ux-mockup: what names its progress to the fidelity-progress tools and its guidance to
  // the actions.
  get slug(): string {
    return this.progress.fidelity.slug
  }

  // The fidelity's own name as the session card shows it, such as Scenarios or Front end code, from the board's label;
  // a name too long for the card's column is shortened, so every state lines up after it.
  get name(): string {
    const words = this.label.replace(/[-_]/g, ' ')
    const name = words.charAt(0).toUpperCase() + words.slice(1)
    return SHORT_NAMES[name] ?? name
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

  // What the Python FidelityProgress names next: the first of generate and validate not done, which is validate again
  // while it has violations; nothing once it is done.
  get nextAction(): string {
    return this.progress.next_action
  }

  // The session.json of the ticket's session, which the session tools name it by.
  get sessionFile(): string {
    return this.ticket.session.session_file
  }

  // The practice root this fidelity's files are written under, as the ticket's session holds it.
  get folder(): string {
    return this.ticket.session.practices[this.progress.practice.key]?.root ?? ''
  }

  // The app that edits this fidelity's files, as the board sends its practice: the Story UI editor for every Stories
  // file, none for a practice no app edits.
  get editor(): AppData | null {
    return this.practice?.editor ?? null
  }

  get #look(): (typeof LOOKS)[string] {
    return LOOKS[this.progress.state] ?? LOOKS.not_started
  }
}

// The states from least to most done, so a practice's dot shows its least finished fidelity; violations count as less
// done than work under way, so they are never hidden behind it.
const STATES_BY_PROGRESS = ['violations', 'not_started', 'in_progress', 'done']

// One practice's dot on the chat bar: its fidelities in every stage shown, one dot however many stages show. While the
// practice is on it is shaded by the least finished of them and carries their violations together; while it is off it
// is faint. A press turns the practice on or off for the session.
export class PracticeDotClient {
  constructor(
    readonly practice: string,
    readonly fidelities: FidelityProgressClient[],
    readonly isOn: boolean,
  ) {}

  // The session.json of the ticket's session, which a press on the dot turns the practice on or off in.
  get sessionFile(): string {
    return this.least.sessionFile
  }

  get least(): FidelityProgressClient {
    const rank = (fidelity: FidelityProgressClient) => STATES_BY_PROGRESS.indexOf(fidelity.state)
    return [...this.fidelities].sort((one, other) => rank(one) - rank(other))[0]!
  }

  get shade(): string {
    return this.isOn ? this.least.shade : `${this.least.colour}${OFF_SHADE}`
  }

  get violationCount(): number {
    return this.isOn ? this.fidelities.reduce((count, fidelity) => count + fidelity.violationCount, 0) : 0
  }

  // The first fidelity with violations, whose validation report a press on the count opens.
  get violating(): FidelityProgressClient | undefined {
    return this.isOn ? this.fidelities.find(fidelity => fidelity.violationCount > 0) : undefined
  }
}

// How faint a practice turned off draws its dot.
const OFF_SHADE = '30'
