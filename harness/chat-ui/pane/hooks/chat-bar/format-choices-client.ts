import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { FormatChoiceJson, FormatChoicesJson } from '../../types'
import { callTool, type ChatBarClient } from './chat-bar-client'

// The format chips beside the action button, as the board's action bar has them: Python's ticket.format_choices answers
// a chip for each group of formats the fidelities offer, and the bar keeps only what a person picks. Until a person
// picks, the chips Python marks starts_picked are on. Atom formatChoices, declared in pane/types/index.d.ts.
const formatChoices = atom({ plugin: 'cdd-board', key: 'formatChoices' } as const, { key: '', choices: [], picked: null } as FormatChoicesJson)

export type FormatChips = { choices: FormatChoiceJson[]; picked: string[] }

function keyOf(chatBar: ChatBarClient): string {
  return [chatBar.ticketName, chatBar.shownStage, ...chatBar.actionFidelities.map(fidelity => fidelity.slug)].join(' ')
}

// The chips for the fidelities the action button acts on, read from Python again only when those fidelities change.
export async function currentFormatChips($: EngineInterface, chatBar: ChatBarClient): Promise<FormatChips> {
  const key = keyOf(chatBar)
  let held = (await read($, formatChoices)) ?? { key: '', choices: [], picked: null }
  if (held.key !== key && chatBar.ticketName && chatBar.actionFidelities.length) {
    try {
      const choices = await callTool<FormatChoiceJson[]>($, 'ticket.format_choices', { ticket: chatBar.ticketName, fidelities: chatBar.actionFidelities.map(fidelity => fidelity.slug) })
      held = { key, choices, picked: null }
    } catch {
      held = { key, choices: [], picked: null }
    }
    await update($, formatChoices, () => held)
  }
  return { choices: held.choices, picked: held.picked ?? held.choices.filter(choice => choice.starts_picked).map(choice => choice.label) }
}

// A press on a chip turns it on or off.
export async function toggleFormat($: EngineInterface, chips: FormatChips, label: string): Promise<void> {
  const picked = chips.picked.includes(label) ? chips.picked.filter(each => each !== label) : [...chips.picked, label]
  await update($, formatChoices, held => ({ ...(held ?? { key: '', choices: [] }), picked }))
}

// What the command adds for the chips picked, on an action that takes formats, each format once; nothing otherwise.
export function formatArgumentOf(chatBar: ChatBarClient, chips: FormatChips, action: string): string {
  if (!chatBar.actionsWithFormats.includes(action)) return ''
  const formats = [...new Set(chips.choices.filter(choice => chips.picked.includes(choice.label)).flatMap(choice => choice.formats))]
  return formats.length ? ` format=${formats.join(',')}` : ''
}

// Once an action ran, the chips go back to the ones Python picks, as the board's bar does.
export async function resetFormats($: EngineInterface): Promise<void> {
  await update($, formatChoices, held => ({ ...(held ?? { key: '', choices: [] }), picked: null }))
}
