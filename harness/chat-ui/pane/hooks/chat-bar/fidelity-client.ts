import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ActionStatesData, FidelityProgressData } from '@cdd/harness/kanban/fidelity-progress'

import { commandOf } from '../chat-command'
import { reasonOf } from '../failure'
import { closeActionPicker } from './action-picker-client'
import { callTool, currentChatBar, refreshChatBar, type ChatBarClient } from './chat-bar-client'

const selectedFidelity = atom({ plugin: 'cdd-board', key: 'selectedFidelity' } as const, null as string | null)

// The canvas's practice colours and progress looks (design/StageStrip.dc.html).
const PRACTICE_COLOURS: Record<string, string> = { stories: '#6BCB77', ddd: '#6C5CE7', ux: '#E84393', clean_engineering: '#4FC3F7', bdd: '#00B894' }
const LOOKS: Record<string, { mark: string; word: string; colour: string; shade: string }> = {
  not_started: { mark: '○', word: 'to do', colour: '#71717A', shade: '40' },
  in_progress: { mark: '…', word: 'doing', colour: '#F59E0B', shade: '80' },
  violations: { mark: '✕', word: 'violations', colour: '#EF4444', shade: 'FF' },
  validated: { mark: '◎', word: 'to review', colour: '#E8E8ED', shade: 'C0' },
  done: { mark: '✓', word: 'done', colour: '#22C55E', shade: 'FF' },
}
export const BUILDER_ACTIONS = ['generate', 'validate', 'review', 'iterate', 'sketch', 'render', 'document']
export const ACTION_ICONS: Record<string, string> = { generate: '✦', validate: '◎', review: '✓', satisfy: '✚', iterate: '↻', sketch: '✎', render: '⇄', document: '▭', advance: '→' }

export type FidelityJson = {
  slug: string
  practice: string
  name: string
  progress: string
  violationCount: number
  actions: ActionStatesData
  defaultFormat: string
  nextAction: string
  isSelected: boolean
  folder: string
}

// A practice fidelity of the shown stage, shaded by its progress as on the board.
export class FidelityClient {
  constructor(private readonly json: FidelityJson) {}

  get fidelity(): string {
    return this.json.slug
  }

  get practice(): string {
    return this.json.practice
  }

  // The fidelity's own name as the session card shows it, such as Scenarios or Front end code.
  get name(): string {
    const words = this.json.name.replace(/-/g, ' ')
    return words.charAt(0).toUpperCase() + words.slice(1)
  }

  // The name the actions take, such as ux-mockup: the fidelity's slug.
  get guidance(): string {
    return this.json.slug
  }

  // A fidelity validated and waiting for review reads to review, as on the canvas.
  get status(): string {
    const { progress, actions } = this.json
    return progress === 'in_progress' && actions.validate === 'done' && actions.review !== 'done' ? 'validated' : progress
  }

  get word(): string {
    return this.status === 'violations' ? `${this.violationCount} violations` : LOOKS[this.status].word
  }

  get mark(): string {
    return LOOKS[this.status].mark
  }

  get lookColour(): string {
    return LOOKS[this.status].colour
  }

  get colour(): string {
    return PRACTICE_COLOURS[this.practice] ?? '#9B9BA8'
  }

  // The practice colour, fainter the less is done.
  get shade(): string {
    return `${this.colour}${LOOKS[this.status].shade}`
  }

  get violationCount(): number {
    return this.json.violationCount
  }

  get isSelected(): boolean {
    return this.json.isSelected
  }

  // What the Python Ticket names next on this fidelity: satisfy while it has violations, else the first of generate,
  // validate and review not done; nothing once it is done.
  get nextAction(): string {
    return this.json.nextAction
  }

  // The practice root this fidelity's files are written under.
  get folder(): string {
    return this.json.folder
  }

  get defaultFormat(): string {
    return this.json.defaultFormat
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
export async function selectFidelity($: EngineInterface, fidelity: FidelityClient): Promise<void> {
  await update($, selectedFidelity, () => fidelity.fidelity)
}

// Choosing from the picker runs that action on the fidelity in place of its next one. Review is recorded as the action
// button records it, never run as a command.
export async function chooseAction($: EngineInterface, fidelity: FidelityClient, action: string): Promise<void> {
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
// the chat that runs it can have another session open. Generate writes in the stage's default format.
function actionCommand(chatBar: ChatBarClient, fidelity: FidelityClient, action: string): string {
  const format = action === 'generate' && fidelity.defaultFormat ? ` format=${fidelity.defaultFormat}` : ''
  return `/actions-${action} ${fidelity.guidance}${format} session=${chatBar.sessionFile}`
}

// Generate renders the earlier fidelity first itself when that fidelity has no file in the format.
export async function runAction($: EngineInterface, fidelity: FidelityClient, action: string): Promise<void> {
  await runCommand($, actionCommand(await currentChatBar($), fidelity, action))
}

// Review is the person's own approval, recorded by the Python Ticket, which refuses it until the latest Validate passed.
export async function reviewFidelity($: EngineInterface, fidelity: FidelityClient): Promise<FidelityClient | ReviewRefused> {
  const chatBar = await currentChatBar($)
  try {
    await callTool<FidelityProgressData>($, 'fidelity-progress.finish_review', { ticket: chatBar.sessionName, fidelity: fidelity.fidelity })
  } catch (failure) {
    $.ui.toast(`${fidelity.guidance} not reviewed: ${reasonOf(failure)}`)
    return new ReviewRefused(reasonOf(failure))
  }
  $.ui.toast(`${fidelity.fidelity} reviewed on ${chatBar.sessionName}`)
  await refreshChatBar($)
  return (await currentChatBar($)).fidelities.find(entry => entry.fidelity === fidelity.fidelity) ?? fidelity
}

// A dot opens the board on this session at that fidelity, and the action button follows it.
export async function openBoard($: EngineInterface, fidelity: FidelityClient): Promise<void> {
  await selectFidelity($, fidelity)
  const chatBar = await currentChatBar($)
  await runCommand($, `/board ${chatBar.sessionName} ${fidelity.fidelity}`)
}
