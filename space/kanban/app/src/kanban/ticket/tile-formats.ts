import type { FidelityGuidanceData } from '@cdd/space/kanban/board'

import { FORMAT_GROUPS } from '../board/board-brand'
import type { FilesByFidelity } from './ticket-client'

export type FormatChip = { label: string; formats: string[] }

const formatsOf = (fidelity: FidelityGuidanceData): string[] => Object.keys(fidelity.outputs)

// Each group the tile offers, and any format the canvas groups do not name under its own name.
export function chipsOf(fidelities: FidelityGuidanceData[]): FormatChip[] {
  const offered = [...new Set(fidelities.flatMap(formatsOf))]
  const grouped = FORMAT_GROUPS.map(group => ({ ...group, formats: group.formats.filter(format => offered.includes(format)) })).filter(group => group.formats.length)
  const named = FORMAT_GROUPS.flatMap(group => group.formats)
  const others = offered.filter(format => !named.includes(format)).map(format => ({ label: format, formats: [format] }))
  return [...grouped, ...others]
}

// A chip stands for a group, and each fidelity uses one format from it: its default when the group holds that.
function chipFormat(fidelity: FidelityGuidanceData, chip: FormatChip): string | undefined {
  const offered = chip.formats.filter(format => formatsOf(fidelity).includes(format))
  return offered.includes(fidelity.default_format) ? fidelity.default_format : offered[0]
}

export function chosenFormats(fidelities: FidelityGuidanceData[], picked: string[]): string[] {
  const chips = chipsOf(fidelities).filter(chip => picked.includes(chip.label))
  return [...new Set(fidelities.flatMap(fidelity => chips.flatMap(chip => chipFormat(fidelity, chip) ?? [])))]
}

// A fidelity's files are read through its progress on the ticket, which names it by its slug.
const hasMade = (files: FilesByFidelity, fidelity: FidelityGuidanceData, chip: FormatChip): boolean =>
  chip.formats.some(format => (files[fidelity.slug]?.[format] ?? []).some(entry => entry.exists))

export const chipDoneCount = (files: FilesByFidelity, fidelities: FidelityGuidanceData[], chip: FormatChip): number => fidelities.filter(fidelity => hasMade(files, fidelity, chip)).length

export const chipOfferedCount = (fidelities: FidelityGuidanceData[], chip: FormatChip): number => fidelities.filter(fidelity => chipFormat(fidelity, chip)).length

// A tile opens ready to run: the fidelities' default formats, unless that output already exists.
export function defaultPicks(fidelities: FidelityGuidanceData[], files: FilesByFidelity): string[] {
  const defaults = fidelities.map(fidelity => fidelity.default_format)
  return chipsOf(fidelities)
    .filter(chip => chip.formats.some(format => defaults.includes(format)) && !chipDoneCount(files, fidelities, chip))
    .map(chip => chip.label)
}
