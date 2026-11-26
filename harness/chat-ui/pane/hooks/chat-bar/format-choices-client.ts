import type { FormatChoiceJson } from '../../types'
import type { ChatBarClient } from './chat-bar-client'

// The format chips beside the action button: each format group the selected fidelities offer, selected or not, as the
// session's guidance selection holds them (ChatBarClient.formatChoices), the same chips the Files app shows; and the
// group a press is filtering by now, whose chip shows the busy wheel until the answer lands.
export type FormatChips = { choices: FormatChoiceJson[]; filtering: string; wheel: string }

const FORMAT_PART = 'format:'

// pressed is the press running now as part:name (currentPressedGuidance), wheel the busy wheel's frame.
export function currentFormatChips(chatBar: ChatBarClient, pressed: string, wheel: string): FormatChips {
  return { choices: chatBar.formatChoices, filtering: pressed.startsWith(FORMAT_PART) ? pressed.slice(FORMAT_PART.length) : '', wheel }
}
