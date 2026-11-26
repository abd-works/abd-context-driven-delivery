import type { FormatChoiceJson } from '../../types'
import type { ChatBarClient } from './chat-bar-client'

// The format chips beside the action button: each format group the selected fidelities offer, selected or not, as the
// session's guidance selection holds them (ChatBarClient.formatChoices), the same chips the Files app shows.
export type FormatChips = { choices: FormatChoiceJson[] }

export function currentFormatChips(chatBar: ChatBarClient): FormatChips {
  return { choices: chatBar.formatChoices }
}
