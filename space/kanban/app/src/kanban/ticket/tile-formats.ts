import type { FormatChoiceData } from '@cdd/space/kanban/ticket'

// Python answers each chip of a bar: its group, the format each fidelity uses from it, how many fidelities offer it and
// have a file in it already, and whether the bar opens with it picked. The page only keeps what a person picks.

// The formats a command sends for the chips picked, each once.
export const chosenFormats = (choices: FormatChoiceData[], picked: string[]): string[] => [
  ...new Set(choices.filter(choice => picked.includes(choice.label)).flatMap(choice => choice.formats)),
]

// The chips a bar opens with picked, ready to run.
export const startingPicks = (choices: FormatChoiceData[]): string[] => choices.filter(choice => choice.starts_picked).map(choice => choice.label)
