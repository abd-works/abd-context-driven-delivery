import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { FormatChoiceJson, FormatChoicesJson } from '../../types'
import { callTool, type ChatBarClient } from './chat-bar-client'

// The format chips beside the action button, as the board's action bar has them: Python's ticket.format_choices answers
// a chip for each group of formats the fidelities offer, each marked is_chosen while the session keeps that format
// chosen for every fidelity in it. A press turns the chip on or off in the session (ticket.choose_formats), the same
// choice the Story UI's format toggles make, so the bar keeps no picks of its own. Atom formatChoices, declared in
// pane/types/index.d.ts.
const formatChoices = atom({ plugin: 'cdd-board', key: 'formatChoices' } as const, { key: '', choices: [] } as FormatChoicesJson)

// The chips read for each set of fidelities this run of the mod, so going back to a set shows its chips at once. A
// generate changes which formats are made, and a Story UI toggle which are chosen, so the board refresh after a cdd tool
// call empties it.
const CACHE = new Map<string, FormatChoiceJson[]>()

export function forgetFormatChips(): void {
  CACHE.clear()
}

export type FormatChips = { choices: FormatChoiceJson[] }

function keyOf(chatBar: ChatBarClient): string {
  return [chatBar.ticketName, chatBar.shownStage, ...chatBar.actionFidelities.map(fidelity => fidelity.slug)].join(' ')
}

// The chips for the fidelities the action button acts on, as last read. Drawing only reads: until loadFormatChips has
// read the chips for new fidelities, the bar keeps showing the last chips, so they never blink out.
export async function currentFormatChips($: EngineInterface, chatBar: ChatBarClient): Promise<FormatChips> {
  const held = (await read($, formatChoices)) ?? { key: '', choices: [] }
  const cached = CACHE.get(keyOf(chatBar))
  return { choices: held.key !== keyOf(chatBar) && cached ? cached : held.choices }
}

// Read the chips again when the fidelities the action button acts on have changed; called from events, never a draw.
export async function loadFormatChips($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  const key = keyOf(chatBar)
  const held = await read($, formatChoices)
  if (held?.key === key || !chatBar.ticketName || !chatBar.actionFidelities.length) return
  let choices = CACHE.get(key)
  if (!choices) {
    try {
      choices = await callTool<FormatChoiceJson[]>($, 'ticket.format_choices', { ticket: chatBar.ticketName, fidelities: fidelitySlugsOf(chatBar) })
    } catch {
      return
    }
    CACHE.set(key, choices)
  }
  await update($, formatChoices, () => ({ key, choices }))
}

// A press on a chip turns it on or off in the session; the bar shows the chips Python answers.
export async function toggleFormat($: EngineInterface, chatBar: ChatBarClient, chips: FormatChips, label: string): Promise<void> {
  const chip = chips.choices.find(choice => choice.label === label)
  if (!chip) return
  const key = keyOf(chatBar)
  const choices = await callTool<FormatChoiceJson[]>($, 'ticket.choose_formats', { ticket: chatBar.ticketName, fidelities: fidelitySlugsOf(chatBar), label, is_chosen: !chip.is_chosen })
  CACHE.set(key, choices)
  await update($, formatChoices, () => ({ key, choices }))
}

// What the command adds for the chips chosen, on an action that takes formats, each format once; nothing otherwise.
export function formatArgumentOf(chatBar: ChatBarClient, chips: FormatChips, action: string): string {
  if (!chatBar.actionsWithFormats.includes(action)) return ''
  const formats = [...new Set(chips.choices.filter(choice => choice.is_chosen).flatMap(choice => choice.formats))]
  return formats.length ? ` format=${formats.join(',')}` : ''
}

function fidelitySlugsOf(chatBar: ChatBarClient): string[] {
  return chatBar.actionFidelities.map(fidelity => fidelity.slug)
}
