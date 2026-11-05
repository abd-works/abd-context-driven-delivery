import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ActionStatesData, FileEntryData, FileTextData, TicketData } from '@cdd/harness/kanban/ticket'

import type { ActionPickerJson, FidelityFilesJson } from '../../types'
import { callTool, currentChatBar, refreshChatBar } from './chat-bar-client'

const selectedFidelity = atom({ plugin: 'cdd-board', key: 'selectedFidelity' } as const, null as string | null)
const actionPicker = atom({ plugin: 'cdd-board', key: 'actionPicker' } as const, { isOpen: false } as ActionPickerJson)
const fidelityFiles = atom({ plugin: 'cdd-board', key: 'fidelityFiles' } as const, null as FidelityFilesJson)

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
const STEPS: (keyof ActionStatesData)[] = ['generate', 'validate', 'review']
// The files view orders a fidelity's files as the board does: markdown, then code, then diagrams.
const fileOrder = (path: string): number => (path.endsWith('.md') ? 0 : path.endsWith('.drawio') ? 2 : 1)
const reasonOf = (error: unknown): string => (error instanceof Error ? error.message : String(error))

export type FidelityJson = {
  slug: string
  progress: string
  violationCount: number
  actions: ActionStatesData
  defaultFormat: string
  nextOfTicket: string
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
    return this.json.slug.slice(0, this.json.slug.indexOf('-'))
  }

  // The fidelity's own name as the session card shows it, such as Scenarios or Front end code.
  get name(): string {
    const words = this.json.slug.slice(this.json.slug.indexOf('-') + 1).replace(/_/g, ' ')
    return words.charAt(0).toUpperCase() + words.slice(1)
  }

  // The name the actions take, such as ux-mockup.
  get guidance(): string {
    return this.json.slug.replace(/_/g, '-')
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

  // The ticket's own next step when this fidelity is next, otherwise the first of generate, validate and review left to do.
  get nextAction(): string {
    return this.json.nextOfTicket || (STEPS.find(step => this.json.actions[step] !== 'done') ?? 'review')
  }

  // The practice root this fidelity's files are written under.
  get folder(): string {
    return this.json.folder
  }

  get defaultFormat(): string {
    return this.json.defaultFormat
  }
}

// ticket.finish_review refused the review, most often because the latest Validate did not pass. reason is the server's text.
export class ReviewRefused {
  constructor(readonly reason: string) {}
}

// Atom selectedFidelity, declared in pane/types/index.d.ts and kept in this file.
export function selectedFidelitySlug($: EngineInterface) {
  return read($, selectedFidelity)
}

export async function currentFidelity($: EngineInterface): Promise<FidelityClient | null> {
  return (await currentChatBar($)).selectedFidelity
}

export function currentActionPicker($: EngineInterface) {
  return read($, actionPicker)
}

export function currentFidelityFiles($: EngineInterface) {
  return read($, fidelityFiles)
}

// Selecting one fidelity replaces the last, so one dot is selected at most.
export async function selectFidelity($: EngineInterface, fidelity: FidelityClient): Promise<void> {
  await update($, selectedFidelity, () => fidelity.fidelity)
}

export async function toggleActionPicker($: EngineInterface): Promise<void> {
  await update($, actionPicker, picker => ({ ...picker, isOpen: !picker.isOpen }))
}

// Choosing from the picker runs that action on the fidelity in place of its next one.
export async function chooseAction($: EngineInterface, fidelity: FidelityClient, action: string): Promise<void> {
  await update($, actionPicker, () => ({ isOpen: false }))
  await runAction($, fidelity, action)
}

async function runCommand($: EngineInterface, text: string): Promise<void> {
  const [name = '', ...words] = text.slice(1).split(' ')
  try {
    await $.command.run({ command: name, args: words.join(' ') })
  } catch (failure) {
    $.ui.toast(`The chat would not run ${text}: ${reasonOf(failure)}`)
  }
}

// Generate can take two commands, a render and then the generate, so ticket.generate_commands names them.
export async function runAction($: EngineInterface, fidelity: FidelityClient, action: string): Promise<void> {
  if (action !== 'generate') return runCommand($, `/actions-${action} ${fidelity.guidance}`)
  const bar = await currentChatBar($)
  const formats = fidelity.defaultFormat ? [fidelity.defaultFormat] : []
  try {
    const commands = await callTool<string[]>($, 'ticket.generate_commands', { ticket: bar.sessionName, fidelities: [fidelity.fidelity], formats })
    for (const command of commands) await runCommand($, command)
  } catch (failure) {
    $.ui.toast(`${fidelity.guidance} cannot generate: ${reasonOf(failure)}`)
  }
}

// Review is the person's own approval, recorded by the Python Ticket, which refuses it until the latest Validate passed.
export async function reviewFidelity($: EngineInterface, fidelity: FidelityClient): Promise<FidelityClient | ReviewRefused> {
  const bar = await currentChatBar($)
  try {
    await callTool<TicketData>($, 'ticket.finish_review', { ticket: bar.sessionName, fidelities: [fidelity.fidelity] })
  } catch (failure) {
    $.ui.toast(`${fidelity.guidance} not reviewed: ${reasonOf(failure)}`)
    return new ReviewRefused(reasonOf(failure))
  }
  $.ui.toast(`${fidelity.fidelity} reviewed on ${bar.sessionName}`)
  await refreshChatBar($)
  return (await currentChatBar($)).fidelities.find(entry => entry.fidelity === fidelity.fidelity) ?? fidelity
}

// One tab per file the fidelity declares; the first tab's text is read straight away.
export async function openFiles($: EngineInterface, fidelity: FidelityClient): Promise<void> {
  const bar = await currentChatBar($)
  try {
    const files = await callTool<Record<string, Record<string, FileEntryData[]>>>($, 'ticket.files', { ticket: bar.sessionName, fidelities: [fidelity.fidelity] })
    const paths = [...new Set(Object.values(files[fidelity.fidelity] ?? {}).flat().map(entry => entry.path))].sort((a, b) => fileOrder(a) - fileOrder(b))
    await update($, fidelityFiles, () => ({ fidelity: fidelity.fidelity, tabs: paths.map(path => ({ path, text: null })), shown: paths[0] ?? null }))
    if (paths[0]) await showFile($, paths[0])
  } catch (failure) {
    $.ui.toast(`${fidelity.guidance} files: ${reasonOf(failure)}`)
  }
}

// A file the server refuses shows the server's reason in its tab.
export async function showFile($: EngineInterface, path: string): Promise<void> {
  const bar = await currentChatBar($)
  let text: string
  try {
    text = (await callTool<FileTextData>($, 'ticket.read_file', { ticket: bar.sessionName, path })).text
  } catch (failure) {
    text = reasonOf(failure)
  }
  await update($, fidelityFiles, files => (files ? { ...files, shown: path, tabs: files.tabs.map(tab => (tab.path === path ? { path, text } : tab)) } : files))
}

export async function closeFiles($: EngineInterface): Promise<void> {
  await update($, fidelityFiles, () => null)
}

// A dot opens the board on this session at that fidelity, and the action button follows it.
export async function openBoard($: EngineInterface, fidelity: FidelityClient): Promise<void> {
  await selectFidelity($, fidelity)
  const bar = await currentChatBar($)
  await runCommand($, `/board ${bar.sessionName} ${fidelity.fidelity}`)
}
