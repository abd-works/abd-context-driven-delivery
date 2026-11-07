import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { PracticeGuidanceData } from '@cdd/space/kanban/board'
import type { FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import type { TicketData } from '@cdd/space/kanban/ticket'

import { commandOf } from '../chat-command'
import { reasonOf } from '../failure'
import { closeActionPicker } from './action-picker-client'
import { callTool, currentChatBar, refreshChatBar, type ChatBarClient } from './chat-bar-client'

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
    return this.progress.slug
  }

  // The fidelity's own name as the session card shows it, such as Scenarios or Front end code.
  get name(): string {
    const words = this.progress.fidelity.name.replace(/_/g, ' ')
    return words.charAt(0).toUpperCase() + words.slice(1)
  }

  get word(): string {
    return this.progress.state === 'violations' ? `${this.violationCount} violations` : this.#look.word
  }

  get mark(): string {
    return this.#look.mark
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

  // What the Python FidelityProgress names next: satisfy while it has violations, else the first of generate, validate
  // and review not done; nothing once it is done.
  get nextAction(): string {
    return this.progress.next_action
  }

  // The practice root this fidelity's files are written under, as the ticket's session holds it.
  get folder(): string {
    return this.ticket.session.practices[this.progress.practice]?.root ?? ''
  }

  get defaultFormat(): string {
    return this.progress.fidelity.default_format
  }

  get #look(): (typeof LOOKS)[string] {
    return LOOKS[this.progress.state] ?? LOOKS.not_started
  }
}

// fidelity-progress.finish_review refused the review, most often because the latest Validate did not pass. reason is the server's text.
export class ReviewRefused {
  constructor(readonly reason: string) {}
}

// Atom selectedFidelity, declared in pane/types/index.d.ts and kept in this file.
export function selectedFidelitySlug($: EngineInterface) {
  return read($, selectedFidelity)
}

// Selecting one fidelity replaces the last, so one dot is selected at most.
export async function selectFidelity($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  await update($, selectedFidelity, () => fidelity.slug)
}

// Choosing from the picker runs that action on the fidelity in place of its next one. Review is recorded as the action
// button records it, never run as a command.
export async function chooseAction($: EngineInterface, fidelity: FidelityProgressClient, action: string): Promise<void> {
  await closeActionPicker($)
  if (action === 'review') await reviewFidelity($, fidelity)
  else await runAction($, fidelity, action)
}

async function runCommand($: EngineInterface, text: string): Promise<void> {
  try {
    await $.command.run(commandOf(text))
  } catch (failure) {
    $.ui.toast(`The chat would not run ${text}: ${reasonOf(failure)}`)
  }
}

// The one place a chat bar command names its session: every action command names the ticket's session.json, because
// the chat that runs it can have another session open. Generate writes in the fidelity's default format.
function actionCommand(chatBar: ChatBarClient, fidelity: FidelityProgressClient, action: string): string {
  const format = action === 'generate' && fidelity.defaultFormat ? ` format=${fidelity.defaultFormat}` : ''
  return `/actions-${action} ${fidelity.slug}${format} session=${chatBar.sessionFile}`
}

// Generate renders the earlier fidelity first itself when that fidelity has no file in the format.
export async function runAction($: EngineInterface, fidelity: FidelityProgressClient, action: string): Promise<void> {
  await runCommand($, actionCommand(await currentChatBar($), fidelity, action))
}

// Review is the person's own approval, recorded by the Python FidelityProgress, which refuses it until the latest
// Validate passed.
export async function reviewFidelity($: EngineInterface, fidelity: FidelityProgressClient): Promise<FidelityProgressClient | ReviewRefused> {
  const { ticket, slug } = fidelity.progress
  try {
    await callTool<FidelityProgressData>($, 'fidelity-progress.finish_review', { ticket, fidelity: slug })
  } catch (failure) {
    $.ui.toast(`${slug} not reviewed: ${reasonOf(failure)}`)
    return new ReviewRefused(reasonOf(failure))
  }
  $.ui.toast(`${slug} reviewed on ${ticket}`)
  await refreshChatBar($)
  return (await currentChatBar($)).fidelities.find(entry => entry.slug === slug) ?? fidelity
}

// A dot opens the board on this session at that fidelity, and the action button follows it.
export async function openBoard($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  await selectFidelity($, fidelity)
  await runCommand($, `/board ${fidelity.progress.ticket} ${fidelity.slug}`)
}
