import type { FormatChoiceData } from '@cdd/space/kanban/ticket'

// Python answers each chip of a bar: its group, the format each fidelity uses from it, how many fidelities offer it and
// have a file in it already, and whether the session keeps it chosen. The page keeps no picks of its own: a press
// chooses in the session, the same choice the chat bar's chips and the Story UI's toggles make.

// The formats a command sends for the chips chosen, each once.
export const chosenFormats = (choices: FormatChoiceData[]): string[] => [...new Set(choices.filter(choice => choice.is_chosen).flatMap(choice => choice.formats))]
