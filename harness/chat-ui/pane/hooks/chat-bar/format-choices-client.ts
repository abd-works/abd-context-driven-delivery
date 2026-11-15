import type { FormatChoiceJson } from '../../types'
import type { ChatBarClient } from './chat-bar-client'

// The format chips beside the action button: each format group the selected fidelities offer, selected or not, as the
// session's guidance selection holds them (ChatBarClient.formatChoices), the same chips the Files app shows.
export type FormatChips = { choices: FormatChoiceJson[] }

export function currentFormatChips(chatBar: ChatBarClient): FormatChips {
  return { choices: chatBar.formatChoices }
}

// What the command adds for the chips chosen, on an action that takes formats, each format once; nothing otherwise.
export function formatArgumentOf(chatBar: ChatBarClient, chips: FormatChips, action: string): string {
  if (!chatBar.actionsWithFormats.includes(action)) return ''
  const formats = [...new Set(chips.choices.filter(choice => choice.is_chosen).flatMap(choice => choice.formats))]
  return formats.length ? ` format=${formats.join(',')}` : ''
}
